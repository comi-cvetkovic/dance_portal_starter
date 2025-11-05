# core/context_processors.py
from django.contrib.auth.models import AnonymousUser

def navbar_context(request):
    from .models import DanceClub  # adjust if needed
    user = getattr(request, "user", None) or AnonymousUser()

    clubs_pending_count = 0
    user_club = None
    user_club_confirmed = True
    navbar_display_name = ""
    is_judge_user = False

    if getattr(user, "is_authenticated", False):
        # role flags
        is_admin = bool(user.is_staff or user.is_superuser)
        try:
            is_judge_user = (
                getattr(user, "is_judge", False)
                or user.groups.filter(name__iexact="judges").exists()
            )
        except Exception:
            pass

        # display name
        if is_admin:
            navbar_display_name = user.username or user.get_username()
        elif is_judge_user:
            navbar_display_name = (user.first_name or "").strip() or user.username
        else:
            rep = getattr(user, "representative_name", "") or ""
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
    }
