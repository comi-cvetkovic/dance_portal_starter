# core/context_processors.py
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

def navbar_context(request):
    from .models import DanceClub  # adjust if needed
    user = getattr(request, "user", None) or AnonymousUser()
    resolver_match = getattr(request, "resolver_match", None)
    url_name = getattr(resolver_match, "url_name", None) if resolver_match else None
    breadcrumb_label = (url_name or "Page").replace("-", " ").replace("_", " ").title()

    clubs_pending_count = 0
    user_club = None
    user_club_confirmed = True
    navbar_display_name = ""
    is_judge_user = False
    judge_home_url = ""

    if getattr(user, "is_authenticated", False):
        # role flags
        is_admin = bool(user.is_staff or user.is_superuser)
        try:
            is_judge_user = (
                getattr(user, "is_judge", False)
                or (getattr(user, "username", "") or "").startswith("judge_")
                or user.groups.filter(name__iexact="judges").exists()
            )
        except Exception:
            pass

        # display name
        if is_admin:
            navbar_display_name = user.username or user.get_username()
        elif is_judge_user:
            navbar_display_name = (user.first_name or "").strip() or user.username
            try:
                parts = (user.username or "").split("_")
                if len(parts) >= 3 and parts[0] == "judge":
                    event_id = int(parts[1])
                    judge_home_url = f"{reverse('judge_view', args=[event_id])}?group=0"
            except Exception:
                judge_home_url = ""
        else:
            rep = ""
            try:
                user_club = DanceClub.objects.filter(user=user).first()
                rep = (user_club.representative_name if user_club else "") or ""
            except Exception:
                rep = ""
            navbar_display_name = rep.strip() or user.username

        # pending + club state
        try:
            if is_admin:
                from .models import DanceClub
                clubs_pending_count = DanceClub.objects.filter(confirmed=False).count()
            else:
                user_club = DanceClub.objects.filter(user=user).first()
                if user_club:
                    user_club_confirmed = bool(user_club.confirmed)
        except Exception:
            pass

    return {
        "clubs_pending_count": clubs_pending_count,
        "user_club": user_club,
        "user_club_confirmed": user_club_confirmed,
        "navbar_display_name": navbar_display_name,
        "is_judge_user": is_judge_user,       # <-- use this in base.html
        "judge_home_url": judge_home_url,
        "breadcrumb_label": breadcrumb_label,
    }
