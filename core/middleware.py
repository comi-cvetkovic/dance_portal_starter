from django.shortcuts import redirect
from django.urls import reverse


class JudgeAccessMiddleware:
    """
    Restrict judge accounts to the judging page only (+ language switch and logout).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return self.get_response(request)

        username = getattr(user, "username", "") or ""
        if not username.startswith("judge_"):
            return self.get_response(request)

        match = getattr(request, "resolver_match", None)
        url_name = getattr(match, "url_name", "")
        allowed = {"judge_view", "logout", "set_language"}
        if url_name in allowed:
            return self.get_response(request)

        event_id = None
        try:
            parts = username.split("_")
            if len(parts) >= 3 and parts[0] == "judge":
                event_id = int(parts[1])
        except Exception:
            event_id = None

        if event_id is not None:
            return redirect(f"{reverse('judge_view', args=[event_id])}?group=0")
        return redirect("logout")
