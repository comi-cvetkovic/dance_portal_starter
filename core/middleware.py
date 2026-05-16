from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

from .auth_utils import is_judge_account, judge_event_id_from_username


class JudgeAccessMiddleware:
    """
    Keep judge accounts inside the judging flow only.
    This middleware only applies to users detected as judge accounts.
    """

    allowed_url_names = {"judge_view", "logout", "set_language"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if not is_judge_account(user):
            return self.get_response(request)

        resolver_match = getattr(request, "resolver_match", None)
        current_url_name = getattr(resolver_match, "url_name", None)
        if current_url_name in self.allowed_url_names:
            return self.get_response(request)

        event_id = judge_event_id_from_username(getattr(user, "username", ""))
        if not event_id:
            return redirect("logout")

        target = f"{reverse('judge_view', args=[event_id])}?group=0"

        # Avoid loops and avoid mutating non-GET requests.
        if request.path == reverse("judge_view", args=[event_id]):
            return self.get_response(request)
        if request.method not in {"GET", "HEAD"}:
            return HttpResponseForbidden("Judge accounts can only access the judging panel.")
        return redirect(target)
