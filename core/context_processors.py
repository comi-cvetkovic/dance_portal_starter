from .models import DanceClub

def add_pending_club_count(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return {
            'clubs_pending_count': DanceClub.objects.filter(confirmed=False).count()
        }
    return {}