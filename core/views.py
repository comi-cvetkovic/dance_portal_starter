from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from collections import defaultdict
from .models import ( 
    Event, Participation, DanceClub, Dancer, StyleCategory, 
    DancerParticipation, EventPlaybackState, JudgeScore,
    Diploma,
)
from .forms import (
    EventForm,
    ParticipationForm,
    DanceClubRegistrationForm,
    DancerForm,
    GroupParticipationForm,
    JudgeCreationFormSet,
    SingleJudgeForm,
    ClubLoginForm,
)
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from collections import defaultdict
from django.db.models import Q, Prefetch, Max, Avg
from django.contrib import messages
from django.utils.timezone import localtime
from collections import defaultdict, OrderedDict
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from django.contrib.auth.models import User
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import io
import os
from collections import namedtuple
from urllib.parse import unquote
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
from django.conf import settings
from django import forms
from django.utils.translation import gettext as _
from PIL import Image, ImageDraw, ImageFont
from decimal import Decimal
import builtins

# Order definitions
DEFAULT_STYLES = ['Show Dance', 'Contemporary/Modern Dance', 'Lyrical Jazz', 'Jazz Performance', 'Open',
               'Ballet Repertiore', 'Ballet Open', 'Tap', 'Musical Theater Performance', 'Acro',
               'Commercial Performance', 'Heels', 'Frame Up Strip', 'Latin Performance', 'Ballroom/Round Dancing',
               'Street Dance/ Open Freestyle', 'Hip-Hop', 'Break Dance', 'Shuffle Dance', 'Disco Dance', 'Dance Fitness',
               'K-Pop', 'Oriental Dance', 'Indian Classical', 'Bollywood', 'Character Ethnic', 'Majorette', 'Pom-Pom']

STYLE_ORDER = DEFAULT_STYLES
AGE_GROUP_ORDER = ['Baby', 'Mini Kids', 'Kids', 'Teen', 'Youth', 'Adult']
GROUP_TYPE_ORDER = ['Solo', 'Duo', 'Trio', 'Group', 'Formation', 'Production']


class NotifyClubsForm(forms.Form):
    clubs = forms.ModelMultipleChoiceField(
        queryset=DanceClub.objects.filter(confirmed=True),
        widget=forms.CheckboxSelectMultiple
    )
    subject = forms.CharField(max_length=200, initial="New Dance Event Announcement")
    message = forms.CharField(widget=forms.Textarea)

@staff_member_required
def notify_clubs_of_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        form = NotifyClubsForm(request.POST)
        if form.is_valid():
            selected_clubs = form.cleaned_data["clubs"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            recipients = [club.user.email for club in selected_clubs]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)

            messages.success(request, f"Email sent to {len(recipients)} clubs.")
            return redirect("event_list")
    else:
        # Default message with event details
        default_message = (
            f"We are excited to announce a new event!\n\n"
            f"Event: {event.name}\n"
            f"Location: {event.location}, {event.city}\n"
            f"Date: {event.date}\n\n"
            f"We hope to see your dancers participating!"
        )
        form = NotifyClubsForm(initial={"message": default_message})

    return render(request, "core/notify_clubs.html", {"form": form, "event": event})

def get_order_index(value, order_list):
    try:
        return order_list.index(value)
    except ValueError:
        return len(order_list)

@require_POST
@login_required
def calculate_age_group_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # ✅ Use dancers[] and strip blanks
    dancer_ids = [d for d in request.POST.getlist("dancers[]") if d]

    dancers = Dancer.objects.filter(id__in=dancer_ids)

    age_group, avg_age = calculate_age_group(dancers)
    return JsonResponse({
        "age_group": age_group or "",
        "avg_age": avg_age or ""
    })

def calculate_age_group(dancers):
    """Return (age_group_label, average_age) based on dancer DOB(s)."""
    if not dancers:
        return None, None

    today = date.today()
    ages = []
    for d in dancers:
        if d.date_of_birth:
            age = today.year - d.date_of_birth.year - (
                (today.month, today.day) < (d.date_of_birth.month, d.date_of_birth.day)
            )
            ages.append(age)

    if not ages:
        return None, None

    avg_age = sum(ages) / len(ages)

    # Map average age to categories
    if avg_age <= 6:
        group = "Baby"
    elif avg_age <= 8:
        group = "Mini Kids"
    elif avg_age <= 11:
        group = "Kids"
    elif avg_age <= 14:
        group = "Teen"
    elif avg_age <= 17:
        group = "Youth"
    else:
        group = "Adult"

    return group, round(avg_age, 1)

@staff_member_required
def event_music_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    participations = Participation.objects.filter(event=event).select_related("style").order_by(
        "group_display_order", "display_order"
    )

    dancer_participations = DancerParticipation.objects.filter(
        participation__in=participations
    ).select_related("dancer", "dancer__club")

    dancer_map = defaultdict(list)
    for dp in dancer_participations:
        dancer_map[dp.participation_id].append(dp.dancer)

    grouped = OrderedDict()
    group_keys = []

    for p in participations:
        dancers = dancer_map.get(p.id, [])
        club = dancers[0].club if dancers else None

        group_key = (p.style.name, p.group_type, p.age_group, p.difficulty)
        if group_key not in grouped:
            grouped[group_key] = []
            group_keys.append(group_key)

        grouped[group_key].append({
            "id": p.id,
            "style": p.style.name,
            "difficulty": p.difficulty,
            "group_type": p.group_type,
            "age_group": p.age_group,
            "dancers": dancers,
            "group_name": p.group_name,
            "num_dancers": len(dancers),
            "choreographer": p.choreographer_name,
            "choreography_name": p.choreography_name,
            "club_name": club.club_name if club else "–",
            "club_city": club.city if club else "–",
            "music_file_url": p.music_file.url if p.music_file else None,
            "music_file_name": p.music_file.name.split("/")[-1] if p.music_file else "default.mp3",
        })

    current_index = int(request.GET.get("group", 0))
    current_tuple = group_keys[current_index] if current_index < len(group_keys) else None
    current_key = "|".join(current_tuple) if current_tuple else None

    if current_key:
        EventPlaybackState.objects.update_or_create(
            event=event,
            defaults={"current_highlight_key": current_key}
        )

    total_categories = len(group_keys)  # ✅ Added

    return render(request, "core/event_music.html", {
        "event": event,
        "grouped_entries": grouped,
        "current_key": current_key,
        "current_index": current_index,
        "total_categories": total_categories,   # ✅ Added
        "has_next": current_index + 1 < len(group_keys),
        "next_key": group_keys[current_index + 1] if current_index + 1 < len(group_keys) else None,
        "previous_key": group_keys[current_index - 1] if current_index > 0 else None,
    })

@staff_member_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        # Delete everything linked to this event
        JudgeScore.objects.filter(participation__event=event).delete()
        DancerParticipation.objects.filter(participation__event=event).delete()
        Participation.objects.filter(event=event).delete()
        StyleCategory.objects.filter(event=event).delete()
        EventPlaybackState.objects.filter(event=event).delete()

        event.delete()

        messages.success(request, _("Event and all related data deleted successfully."))
        return redirect("event_list")

    return redirect("event_list")

@login_required
def start_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    is_admin = request.user.is_superuser
    show_entries = event.start_list_published or is_admin

    participations = Participation.objects.filter(event=event).select_related("style").order_by(
        "group_display_order", "display_order", "id"
    )

    dancer_participations = DancerParticipation.objects.filter(
        participation__in=participations
    ).select_related("dancer", "dancer__club")

    dancer_map = defaultdict(list)
    for dp in dancer_participations:
        dancer_map[dp.participation_id].append(dp.dancer)

    grouped_entries = OrderedDict()
    group_key_to_index = {}
    global_counter = 1

    # Start time handling
    current_time = None
    if event.start_time:
        current_time = datetime.combine(datetime.today(), event.start_time)

    for p in participations:
        dancers = dancer_map.get(p.id, [])
        club = dancers[0].club if dancers else None
        group_key = (p.style.name, p.group_type, p.age_group, p.difficulty)
        group_index = p.group_display_order or 0

        if group_key not in group_key_to_index:
            group_key_to_index[group_key] = group_index
            grouped_entries[group_key] = []

        display_dancers = p.group_name if not is_admin and len(dancers) > 3 and p.group_name else dancers
        start_time_str = current_time.strftime("%H:%M") if current_time else None

        grouped_entries[group_key].append({
            "id": p.id,
            "style": p.style.name,
            "difficulty": p.difficulty,
            "group_type": p.group_type,
            "age_group": p.age_group,
            "dancers": display_dancers,
            "num_dancers": len(dancers),
            "group_name": p.group_name,
            "choreographer": p.choreographer_name,
            "choreography_name": p.choreography_name,
            "club_name": club.club_name if club else "–",
            "club_city": club.city if club else "–",
            "global_row_number": global_counter,
            "start_time": start_time_str,
        })
        global_counter += 1

        if current_time:
            duration = get_music_duration(p)
            current_time += timedelta(seconds=duration)

    sorted_grouped_entries = OrderedDict(
        sorted(grouped_entries.items(), key=lambda item: group_key_to_index[item[0]])
    )

    # 🔹 Get highlight key from EventPlaybackState
    highlight_key = None
    try:
        highlight_key = EventPlaybackState.objects.get(event=event).current_highlight_key
    except EventPlaybackState.DoesNotExist:
        pass

    return render(request, "core/start_list.html", {
        "event": event,
        "grouped_entries": sorted_grouped_entries if show_entries else {},
        "is_admin": is_admin,
        "is_published": event.start_list_published,
        "show_entries": show_entries,
        "highlight_key": highlight_key,
    })


@user_passes_test(lambda u: u.is_superuser)
def manage_start_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        try:
            new_order = request.POST.getlist("ordered_ids[]")
            for idx, pid in enumerate(new_order):
                Participation.objects.filter(id=int(pid)).update(display_order=idx)
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    participations = Participation.objects.filter(event=event).select_related("style").order_by(
        "group_display_order", "display_order", "id"
    )

    dancer_participations = DancerParticipation.objects.filter(
        participation__in=participations
    ).select_related("dancer", "dancer__club")

    dancer_map = defaultdict(list)
    for dp in dancer_participations:
        dancer_map[dp.participation_id].append(dp.dancer)

    grouped_entries = OrderedDict()
    group_key_to_index = {}
    global_counter = 1

    current_time = None
    if event.start_time:
        current_time = datetime.combine(datetime.today(), event.start_time)

    for p in participations:
        dancers = dancer_map.get(p.id, [])
        club = dancers[0].club if dancers else None
        group_key = (p.style.name, p.group_type, p.age_group, p.difficulty)
        group_index = p.group_display_order or 0

        if group_key not in group_key_to_index:
            group_key_to_index[group_key] = group_index
            grouped_entries[group_key] = []

        start_time_str = current_time.strftime("%H:%M") if current_time else None

        grouped_entries[group_key].append({
            "start_time": start_time_str,
            "id": p.id,
            "style": p.style.name,
            "difficulty": p.difficulty,
            "group_type": p.group_type,
            "age_group": p.age_group,
            "dancers": dancers,
            "num_dancers": len(dancers),
            "group_name": p.group_name,
            "choreographer": p.choreographer_name,
            "choreography_name": p.choreography_name,
            "club_name": club.club_name if club else "–",
            "club_city": club.city if club else "–",
            "global_row_number": global_counter,
        })
        global_counter += 1

        if current_time:
            duration = get_music_duration(p)
            current_time += timedelta(seconds=duration)

    sorted_grouped_entries = OrderedDict(
        sorted(grouped_entries.items(), key=lambda item: group_key_to_index[item[0]])
    )

    # 🔹 Get highlight key from EventPlaybackState
    highlight_key = None
    try:
        highlight_key = EventPlaybackState.objects.get(event=event).current_highlight_key
    except EventPlaybackState.DoesNotExist:
        pass

    return render(request, "core/manage_start_list.html", {
        "event": event,
        "grouped_entries": sorted_grouped_entries,
        "is_admin": True,
        "is_published": event.is_published,
        "show_entries": True,
        "highlight_key": highlight_key,
    })



def get_music_duration(p):
    # Fallback duration if no music or no .duration attribute
    if p.music_file and hasattr(p.music_file, "duration") and p.music_file.duration:
        duration = int(p.music_file.duration)
    else:
        if p.group_type in ["Solo", "Duo", "Trio"]:
            duration = 135  # 2:15
        elif p.group_type in ["Group", "Formation"]:
            duration = 180  # 3:00
        else:
            duration = 240  # Production or undefined

    # Add buffer
    if p.group_type in ["Baby", "Mini"]:
        duration += 60
    else:
        duration += 30

    return duration

@staff_member_required
@require_POST
def publish_start_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    mode = request.POST.get("mode", "default")

    participations = list(Participation.objects.filter(event=event).select_related("style"))

    if mode == "current":
        ordered_json = request.POST.get("ordered_ids_json", "[]")
        try:
            ordered_ids = json.loads(ordered_json)
        except Exception:
            ordered_ids = []

        id_to_order = {int(pid): idx for idx, pid in enumerate(ordered_ids)}

        group_index_map = {}
        current_index = 0

        for pid in ordered_ids:
            try:
                p = Participation.objects.get(id=pid)
                group_key = (p.style.name, p.group_type, p.age_group, p.difficulty)

                if group_key not in group_index_map:
                    group_index_map[group_key] = current_index
                    current_index += 1

                p.display_order = id_to_order[p.id]
                p.group_display_order = group_index_map[group_key]
                p.save(update_fields=["display_order", "group_display_order"])
            except Participation.DoesNotExist:
                continue

        # ✅ Only publish if 'current'
        event.start_list_published = True
        event.save(update_fields=["start_list_published"])
        messages.success(request, _("Start list published successfully."))
    elif mode == "default":
        def group_sort_key(p):
            difficulty_rank = 0 if p.difficulty == 'A' else 1
            return (
                difficulty_rank,
                get_order_index(p.style.name, STYLE_ORDER),
                get_order_index(p.group_type, GROUP_TYPE_ORDER),
                get_order_index(p.age_group, AGE_GROUP_ORDER),
            )

        group_map = defaultdict(list)
        for p in participations:
            key = (p.style.name, p.group_type, p.age_group, p.difficulty)
            group_map[key].append(p)

        sorted_keys = sorted(group_map.keys(), key=lambda key: (
            0 if key[3] == 'A' else 1,
            get_order_index(key[0], STYLE_ORDER),
            get_order_index(key[1], GROUP_TYPE_ORDER),
            get_order_index(key[2], AGE_GROUP_ORDER),
        ))

        for group_index, group_key in enumerate(sorted_keys):
            for p in group_map[group_key]:
                p.group_display_order = group_index
                p.save(update_fields=["group_display_order"])

    else:
        messages.error(request, "Invalid publish mode.")
        return redirect('manage_start_list', event_id=event.id)

    return redirect('manage_start_list', event_id=event.id)


@staff_member_required
@require_POST
def unpublish_start_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.start_list_published = False
    event.save(update_fields=["start_list_published"])
    messages.info(request, _("Start list unpublished."))
    return redirect('manage_start_list', event_id=event.id)


def home(request):
    return render(request, 'core/home.html')


def register_club(request):
    if request.method == 'POST':
        form = DanceClubRegistrationForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, _("Club registered successfully. Awaiting admin approval."))
            return redirect('login')
    else:
        form = DanceClubRegistrationForm()

    # 👇 change label only when registering
    if 'password' in form.fields:
        form.fields['password'].label = _("Password")

    return render(request, 'core/register_club.html', {'form': form})




@staff_member_required
def delete_club(request, club_id):
    club = get_object_or_404(DanceClub, id=club_id)
    user = club.user  # get the associated User
    club.delete()     # delete the club
    user.delete()     # delete the User
    messages.success(request, _("Club deleted successfully."))
    return redirect('club_dashboard')


@login_required
def club_dashboard(request):

    def add_pending_club_count(request):
        from .models import DanceClub
        if request.user.is_authenticated and request.user.is_superuser:
            return {
                'clubs_pending_count': DanceClub.objects.filter(confirmed=False).count()
            }
        return {}
    user = request.user
    if user.is_superuser:
        clubs = DanceClub.objects.all()
        return render(request, 'core/dashboard.html', {'clubs': clubs})
    else:
        try:
            club = DanceClub.objects.get(user=user)
            if not club.confirmed:
                return render(request, 'core/awaiting_confirmation.html')
            return render(request, 'core/dashboard.html', {'club': club})
        except DanceClub.DoesNotExist:
            logout(request)
            return redirect('login')
        
@staff_member_required
def pending_club_requests(request):
    pending_clubs = DanceClub.objects.filter(confirmed=False)

    if request.method == "POST":
        club_id = request.POST.get("club_id")
        action = request.POST.get("action")

        club = get_object_or_404(DanceClub, id=club_id)
        if action == "accept":
            club.confirmed = True
            club.save()
            messages.success(request, _("Club approved successfully."))
        elif action == "decline":
            user = club.user
            club.delete()
            user.delete()
            messages.info(request, _("Club declined and removed."))
        return redirect('pending_club_requests')

    return render(request, "core/pending_club_requests.html", {
        "pending_clubs": pending_clubs
    })


@login_required
def add_dancer(request, club_id=None):
    if request.user.is_superuser and club_id:
        club = get_object_or_404(DanceClub, id=club_id)
    else:
        club = get_object_or_404(DanceClub, user=request.user)

    if request.method == 'POST':
        form = DancerForm(request.POST)
        if form.is_valid():
            dancer = form.save(commit=False)
            dancer.club = club
            dancer.save()
            messages.success(request, _("Dancer added successfully."))
            if request.user.is_superuser:
                return redirect('admin_list_dancers', club_id=club.id)
            else:
                return redirect('list_dancers')
    else:
        form = DancerForm()

    return render(request, 'core/add_dancer.html', {
        'form': form,
        'club': club,
        'is_superuser': request.user.is_superuser,
    })

@login_required
def add_dancer(request, club_id=None):
    if request.user.is_superuser and club_id:
        club = get_object_or_404(DanceClub, id=club_id)
    else:
        club = get_object_or_404(DanceClub, user=request.user)

    if request.method == 'POST':
        form = DancerForm(request.POST)
        if form.is_valid():
            dancer = form.save(commit=False)
            dancer.club = club
            dancer.save()
            messages.success(request, _("Dancer added successfully."))
            if request.user.is_superuser:
                return redirect('admin_list_dancers', club_id=club.id)
            else:
                return redirect('list_dancers')
    else:
        form = DancerForm()

    return render(request, 'core/add_dancer.html', {
        'form': form,
        'club': club,
        'is_superuser': request.user.is_superuser,
    })

@login_required
def list_dancers(request, club_id=None):
    if request.user.is_superuser and club_id:
        club = get_object_or_404(DanceClub, id=club_id)
    else:
        club = get_object_or_404(DanceClub, user=request.user)

    dancers = Dancer.objects.filter(club=club)
    return render(request, 'core/list_dancers.html', {
        'dancers': dancers,
        'club': club,
        'is_superuser': request.user.is_superuser,
    })


@login_required
def delete_dancer(request, dancer_id, club_id=None):
    if request.user.is_superuser and club_id:
        club = get_object_or_404(DanceClub, id=club_id)
    else:
        club = get_object_or_404(DanceClub, user=request.user)

    dancer = get_object_or_404(Dancer, id=dancer_id, club=club)
    dancer.delete()
    messages.success(request, _("Dancer deleted successfully."))

    if request.user.is_superuser:
        return redirect('admin_list_dancers', club_id=club.id)
    else:
        return redirect('list_dancers')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = ClubLoginForm

    def get_success_url(self):
        user = self.request.user

        if user.username.startswith("judge_"):
            try:
                event_id = user.username.split("_")[1]
                return reverse('judge_view', args=[int(event_id)])
            except (IndexError, ValueError):
                return reverse('home')

        elif user.is_superuser:
            return reverse('event_list')

        else:
            return reverse('club_dashboard')


def custom_logout_view(request):
    logout(request)
    return redirect('home')


@staff_member_required
def create_event(request):
    if request.method == 'POST':
        # IMPORTANT: include request.FILES
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()

            # Add default styles for this event
            for style_name in DEFAULT_STYLES:
                StyleCategory.objects.get_or_create(event=event, name=style_name)

            messages.success(request, _("Event created successfully."))
            return redirect('event_list')
    else:
        form = EventForm()

    return render(request, 'core/create_event.html', {'form': form})


@staff_member_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        # IMPORTANT: include request.FILES
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, _("Event updated successfully."))
            return redirect('event_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'core/edit_event.html', {'form': form, 'event': event})

@login_required
def event_list(request):
    events = Event.objects.all()

    # Attach a flag to each event indicating if its judge accounts exist
    for event in events:
        event.has_judges = User.objects.filter(username__startswith=f"judge_{event.id}_").exists()


    return render(request, 'core/event_list.html', {
        'events': events
    })



@login_required
def register_dancer(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user.is_superuser:
        clubs = DanceClub.objects.all()
        club_id = request.GET.get("club_id")
        selected_club = None

        if club_id:
            selected_club = get_object_or_404(DanceClub, id=club_id)

        if not selected_club:
            return render(request, 'core/register_dancer.html', {
                'event': event,
                'clubs': clubs,
                'selected_club': None,
                'form': None,
                'is_superuser': True,
            })
    else:
        selected_club = get_object_or_404(DanceClub, user=request.user)
        clubs = None
        club_id = selected_club.id

    avg_age = None
    age_group = None

    if request.method == 'POST':
        print("DEBUG dancers POST:", request.POST.getlist("dancers"))
        form = GroupParticipationForm(request.POST, request.FILES, club=selected_club, event=event)
        if form.is_valid():
            dancers = form.cleaned_data['dancers']
            age_group, avg_age = calculate_age_group(dancers)

            participation = Participation.objects.create(
                event=event,
                style=form.cleaned_data['style'],
                group_type=form.cleaned_data['group_type'],
                age_group=age_group,  # ✅ auto-assigned
                difficulty=form.cleaned_data['difficulty'],
                choreographer_name=form.cleaned_data['choreographer_name'],
                choreography_name=form.cleaned_data['choreography_name'],
                group_name=form.cleaned_data.get('group_name'),
                music_file=form.cleaned_data.get('music_file')
            )

            # save dancer links
            for dancer in dancers:
                DancerParticipation.objects.create(participation=participation, dancer=dancer)
            messages.success(request, _("Participation registered successfully."))
            return redirect(f'{request.path}?club_id={club_id}')
    else:
        form = GroupParticipationForm(club=selected_club, event=event)

    # ✅ Pre-fill age group whenever dancers are selected
    if form.is_bound and form.is_valid():
        dancers = form.cleaned_data.get('dancers')
        age_group, avg_age = calculate_age_group(dancers)
    elif request.method == 'GET' and selected_club:
        # If GET with dancers in query (future: AJAX/JS), calculate too
        pass

    # Force field value & disable editing
    if age_group:
        form.fields['age_group'].initial = age_group
    form.fields['age_group'].disabled = True

    return render(request, 'core/register_dancer.html', {
        'form': form,
        'event': event,
        'clubs': clubs,
        'selected_club': selected_club,
        'is_superuser': request.user.is_superuser,
        'avg_age': avg_age,
    })


@login_required
def list_event_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    view_mode = request.GET.get("view")

    if request.user.is_superuser:
        participations = Participation.objects.filter(event=event)
    else:
        club = get_object_or_404(DanceClub, user=request.user)
        participations = Participation.objects.filter(event=event, dancer_links__dancer__club=club).distinct()

    # 📊 Club Summary Mode
    if request.user.is_superuser and view_mode == "summary":
        clubs = DanceClub.objects.all()
        summary_data = []

        total_counts = {
            "Solo": 0, "Duo": 0, "Trio": 0, "Group": 0, "Formation": 0, "Production": 0,
            "unique_dancer_count": 0,
            "total_dancer_count": 0
        }

        for club in clubs:
            entries = Participation.objects.filter(
                event=event,
                dancer_links__dancer__club=club
            ).distinct()

            group_type_counts = defaultdict(int)
            dancer_ids = set()
            total_dancer_count = 0

            for p in entries:
                group_type_counts[p.group_type] += 1

                linked_dancers = DancerParticipation.objects.filter(
                    participation=p
                ).values_list("dancer_id", flat=True)

                total_dancer_count += len(linked_dancers)
                dancer_ids.update(linked_dancers)

            summary_data.append({
                "club": club,
                "group_type_counts": dict(group_type_counts),
                "unique_dancer_count": len(dancer_ids),
                "total_dancer_count": total_dancer_count
            })

            # Update totals
            for gt in ["Solo", "Duo", "Trio", "Group", "Formation", "Production"]:
                total_counts[gt] += group_type_counts.get(gt, 0)
            total_counts["unique_dancer_count"] += len(dancer_ids)
            total_counts["total_dancer_count"] += total_dancer_count

        return render(request, "core/participant_summary_by_club.html", {
            "event": event,
            "summary_data": summary_data,
            "total_counts": total_counts
        })

    # 🧑‍🎤 Regular participant view
    grouped = defaultdict(list)
    for p in participations:
        key = (
            p.style_id,
            p.group_type,
            p.age_group,
            p.difficulty,
            p.choreographer_name,
        )
        grouped[key].append(p)

    grouped_participations = [
        {
            "style": StyleCategory.objects.get(id=key[0]),
            "group_type": key[1],
            "age_group": key[2],
            "difficulty": key[3],
            "choreographer_name": key[4],
            "choreography_name": plist[0].choreography_name if plist and plist[0].choreography_name else "Untitled",
            "dancers": list({dp.dancer for p in plist for dp in p.dancer_links.all()}),
            "participation_id": plist[0].id,
            "music_file": plist[0].music_file,
        }
        for key, plist in grouped.items()
    ]

    return render(request, 'core/list_event_participants.html', {
        'event': event,
        'grouped_participations': grouped_participations
    })

@staff_member_required
def manage_styles(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    all_style_names = StyleCategory.objects.values_list('name', flat=True).distinct()

    if request.method == 'POST':
        if 'delete_style_id' in request.POST:
            style_id = request.POST.get('delete_style_id')
            StyleCategory.objects.filter(id=style_id, event=event).delete()
        else:
            style_name = request.POST.get('style_name')
            if style_name and not StyleCategory.objects.filter(event=event, name=style_name).exists():
                StyleCategory.objects.create(event=event, name=style_name)
        return redirect('manage_styles', event_id=event.id)

    styles = event.style_categories.all()
    return render(request, 'core/manage_styles.html', {
        'event': event,
        'styles': styles,
        'all_style_names': all_style_names
    })

@login_required
def edit_club(request, club_id=None):
    # Superuser can edit any club, normal user only their own
    if request.user.is_superuser and club_id:
        club = get_object_or_404(DanceClub, id=club_id)
    else:
        club = get_object_or_404(DanceClub, user=request.user)

    if request.method == 'POST':
        form = DanceClubRegistrationForm(request.POST, instance=club)
        if form.is_valid():
            form.save(commit=True)  # form now updates both DanceClub + linked User
            messages.success(request, _("Club details updated successfully."))
            return redirect('club_dashboard')
    else:
        # Pre-fill email from linked user
        form = DanceClubRegistrationForm(
            instance=club,
            initial={'email': club.user.email}
        )

    return render(request, 'core/edit_club.html', {
        'form': form,
        'club': club,
    })

@login_required
def edit_dancer(request, dancer_id):
    dancer = get_object_or_404(Dancer, id=dancer_id)

    if request.user.is_superuser or dancer.club.user == request.user:
        if request.method == 'POST':
            form = DancerForm(request.POST, instance=dancer)
            if form.is_valid():
                form.save()
                messages.success(request, _("Dancer updated successfully."))
                if request.user.is_superuser:
                    return redirect('admin_list_dancers', club_id=dancer.club.id)
                else:
                    return redirect('list_dancers')
        else:
            form = DancerForm(instance=dancer)

        return render(request, 'core/edit_dancer.html', {
            'form': form,
            'dancer': dancer,
            'is_superuser': request.user.is_superuser
        })
    else:
        return redirect('club_dashboard')

@login_required
def edit_participation(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id)
    event = participation.event

    dancers = DancerParticipation.objects.filter(participation=participation).select_related("dancer__club")
    dancer_list = [dp.dancer for dp in dancers]
    club = dancer_list[0].club if dancer_list else None

    if not request.user.is_superuser and (not club or club.user != request.user):
        return redirect('club_dashboard')

    if request.method == 'POST':
        form = GroupParticipationForm(request.POST, request.FILES, club=club, event=event)
        if form.is_valid():
            participation.style = form.cleaned_data['style']
            participation.group_type = form.cleaned_data['group_type']
            participation.age_group = form.cleaned_data['age_group']
            participation.difficulty = form.cleaned_data['difficulty']
            participation.choreographer_name = form.cleaned_data['choreographer_name']
            participation.choreography_name = form.cleaned_data['choreography_name']
            participation.group_name = form.cleaned_data.get('group_name')

            # ✅ Handle music file
            if "remove_music" in request.POST:
                if participation.music_file:
                    participation.music_file.delete(save=False)
                participation.music_file = None
            elif form.cleaned_data.get('music_file'):
                participation.music_file = form.cleaned_data['music_file']

            participation.save()

            # dancers update
            new_dancers = form.cleaned_data['dancers']
            DancerParticipation.objects.filter(participation=participation).exclude(dancer__in=new_dancers).delete()
            for dancer in new_dancers:
                DancerParticipation.objects.get_or_create(participation=participation, dancer=dancer)

            messages.success(request, _("Participation updated successfully."))
            return redirect('list_event_participants', event_id=event.id)
        else:
            messages.error(request, "There was a problem updating the participation. Please correct the errors below.")
    else:
        initial_dancers = DancerParticipation.objects.filter(participation=participation).values_list('dancer_id', flat=True)
        form = GroupParticipationForm(
            club=club,
            event=event,
            initial={
                'dancers': initial_dancers,
                'style': participation.style,
                'group_type': participation.group_type,
                'age_group': participation.age_group,
                'difficulty': participation.difficulty,
                'choreographer_name': participation.choreographer_name,
                'choreography_name': participation.choreography_name,
                'group_name': participation.group_name,
            }
        )

    return render(request, 'core/edit_participation.html', {
        'form': form,
        'participation': participation
    })

    
@login_required
def delete_participation(request):
    if request.method == 'POST':
        event_id = request.POST.get("event_id")
        style_id = request.POST.get("style_id")
        group_type = request.POST.get("group_type")
        age_group = request.POST.get("age_group")
        difficulty = request.POST.get("difficulty")
        choreographer_name = request.POST.get("choreographer_name")

        participations = Participation.objects.filter(
            event_id=event_id,
            style_id=style_id,
            group_type=group_type,
            age_group=age_group,
            difficulty=difficulty,
            choreographer_name=choreographer_name
        )

        # Permission check: allow if user owns the club(s) or is superuser
        if not request.user.is_superuser:
            club = get_object_or_404(DanceClub, user=request.user)
            participations = participations.filter(dancer__club=club)

        event = get_object_or_404(Event, id=event_id)
        participations.delete()
        messages.success(request, _("Participation deleted successfully."))

        return redirect('list_event_participants', event_id=event_id)

    return redirect('event_list')

@login_required
def delete_participation_group(request):
    if request.method == 'POST':
        event_id = request.POST.get("event_id")
        style_id = request.POST.get("style_id")
        group_type = request.POST.get("group_type")
        age_group = request.POST.get("age_group")
        difficulty = request.POST.get("difficulty")
        choreographer_name = request.POST.get("choreographer_name")

        participations = Participation.objects.filter(
            event_id=event_id,
            style_id=style_id,
            group_type=group_type,
            age_group=age_group,
            difficulty=difficulty,
            choreographer_name=choreographer_name
        )

        if not request.user.is_superuser:
            club = get_object_or_404(DanceClub, user=request.user)
            participations = participations.filter(dancer__club=club)

        participations.delete()
        messages.success(request, _("Participation deleted successfully."))
        return redirect('list_event_participants', event_id=event_id)

    return redirect('event_list')

def event_list_public(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'core/event_list_public.html', {'events': events})

@staff_member_required
def create_judges_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        formset = JudgeCreationFormSet(request.POST)
        if formset.is_valid():
            created = []
            for form in formset:
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']

                username = f"judge_{event.id}_{first_name.lower().replace(' ', '').replace('.', '')}"

                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        password=first_name,  # Simplified password
                        first_name=first_name,
                        last_name=last_name,
                        is_staff=False,
                        is_active=True
                    )
                    created.append(username)

            if created:
                messages.success(request, f"Judges created: {', '.join(created)}")
            else:
                messages.info(request, "No new judges created (maybe they already exist).")

            return redirect('event_list')
    else:
        formset = JudgeCreationFormSet()

    existing_judges = User.objects.filter(username__startswith=f"judge_{event.id}_")

    return render(request, "core/manage_judges.html", {
    "event": event,
    "form": form,
    "judges": existing_judges,
})


@login_required
def judge_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Prefetch dancers & clubs for efficiency
    participations = (
        Participation.objects.filter(event=event)
        .select_related("style")
        .prefetch_related("dancer_links__dancer__club")
        .order_by("group_display_order", "display_order", "id")
    )

    # Group participations by category
    grouped = defaultdict(list)
    for p in participations:
        group_key = (p.style.name, p.group_type, p.age_group, p.difficulty)
        grouped[group_key].append(p)

    sorted_keys = sorted(
        grouped.keys(),
        key=lambda k: next(
            (p.group_display_order for p in participations
             if (p.style.name, p.group_type, p.age_group, p.difficulty) == k),
            0
        )
    )

    current_index = int(request.GET.get("group", 0))
    if current_index >= len(sorted_keys):
        current_index = len(sorted_keys) - 1
    if current_index < 0:
        current_index = 0

    current_key = sorted_keys[current_index] if sorted_keys else None
    current_entries = grouped.get(current_key, [])

    all_scored = False

    if request.method == "POST":
        if "review" in request.POST:
            return redirect(f"{reverse('judge_view', args=[event.id])}?group=0")

        # Save multi-criteria scores
        for p in current_entries:
            fields = ["technique", "composition", "image"]
            if p.style.name == "Show Dance":
                fields.append("show_value")

            data = {}
            for f in fields:
                val = request.POST.get(f"{f}_{p.id}")
                if val:
                    data[f] = float(val)

            if data:
                JudgeScore.objects.update_or_create(
                    participation=p,
                    judge=request.user,
                    defaults=data,
                )

        if "next" in request.POST and current_index + 1 < len(sorted_keys):
            return redirect(f"{reverse('judge_view', args=[event.id])}?group={current_index+1}")
        elif "prev" in request.POST and current_index > 0:
            return redirect(f"{reverse('judge_view', args=[event.id])}?group={current_index-1}")
        elif current_index == len(sorted_keys) - 1:
            all_scored = True
        else:
            return redirect(f"{reverse('judge_view', args=[event.id])}?group={current_index}")

    # Load existing scores
    existing_scores = {
        s.participation_id: {
            "technique": s.technique,
            "composition": s.composition,
            "image": s.image,
            "show_value": s.show_value,
        }
        for s in JudgeScore.objects.filter(participation__event=event, judge=request.user)
    }

    context = {
        "event": event,
        "current_key": current_key,
        "current_entries": current_entries,
        "current_index": current_index,
        "total_categories": len(sorted_keys),
        "has_next": current_index + 1 < len(sorted_keys),
        "has_prev": current_index > 0,
        "existing_scores": existing_scores,
        "all_scored": all_scored,
    }
    return render(request, "core/judge_view.html", context)


@staff_member_required
def manage_judges(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    existing_judges = User.objects.filter(username__startswith=f"judge_{event.id}_")

    if request.method == "POST":
        form = SingleJudgeForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = f"judge_{event.id}_{first_name.lower().replace(' ', '').replace('.', '')}"

            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password=first_name,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=False,
                    is_active=True
                )
                messages.success(request, f"Judge {first_name} {last_name} added.")
                return redirect('manage_judges', event_id=event.id)
            else:
                messages.warning(request, "Judge already exists.")
    else:
        form = SingleJudgeForm()

    return render(request, "core/manage_judges.html", {
        "event": event,
        "form": form,
        "judges": existing_judges,
    })

@staff_member_required
@require_POST
def delete_single_judge(request, event_id, judge_id):
    judge = get_object_or_404(User, id=judge_id, username__startswith=f"judge_{event_id}_")
    judge.delete()
    messages.success(request, f"Judge {judge.username} deleted.")
    return redirect('manage_judges', event_id=event_id)


@staff_member_required
@require_POST
def delete_judges_for_event(request, event_id):
    # Delete all judges with the new naming pattern
    User.objects.filter(username__startswith=f"judge_{event_id}_").delete()
    return redirect('event_list')


AwardResult = namedtuple("AwardResult", ["participation", "dancers", "score"])

@login_required
def event_awards_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participations = Participation.objects.filter(event=event).select_related("style")

    judge_scores = JudgeScore.objects.filter(participation__event=event).select_related("participation", "judge")

    # Build dancer map
    dancer_map = defaultdict(list)
    for dp in DancerParticipation.objects.filter(participation__in=participations).select_related("dancer__club"):
        dancer_map[dp.participation_id].append(dp.dancer)

    results_by_category = defaultdict(list)

    for p in participations:
        category_key = (p.style.name, p.group_type, p.age_group, p.difficulty)
        scores = judge_scores.filter(participation=p)

        # Scoring fields
        criterion_fields = ["technique", "composition", "image"]
        if p.style.name == "Show Dance":
            criterion_fields.append("show_value")

        total_points = 0
        total_counts = 0

        for f in criterion_fields:
            values = [getattr(s, f) for s in scores if getattr(s, f) is not None]
            if len(values) >= 3:
                values = sorted(values)[1:-1]  # drop high + low
            total_points += sum(values)
            total_counts += len(values)

        if total_counts > 0:
            final_score = round(total_points / total_counts, 2)
            result = AwardResult(
                participation=p,
                dancers=dancer_map.get(p.id, []),
                score=final_score,
            )
            results_by_category[category_key].append(result)

    # Sort participants within each category by score (descending)
    for category in results_by_category:
        results_by_category[category].sort(key=lambda r: r.score, reverse=True)

    # Preserve category order from start list
    group_display_order_map = {
        (p.style.name, p.group_type, p.age_group, p.difficulty): p.group_display_order or 0
        for p in participations
    }
    
    sorted_keys = sorted(results_by_category.keys(), key=lambda k: group_display_order_map.get(k, 0))

    # Build grouped_results in correct order
    grouped_results = OrderedDict()
    for key in sorted_keys:
        grouped_results[key] = results_by_category[key]

    return render(request, "core/event_awards.html", {
        "event": event,
        "grouped_results": grouped_results,
    })

@staff_member_required
def generate_diploma(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        style, group_type, age_group, difficulty = request.POST.get("category").split("|")

        participations = Participation.objects.filter(
            event=event,
            style__name=style.strip(),
            group_type=group_type.strip(),
            age_group=age_group.strip(),
            difficulty=difficulty.strip(),
        )

        # ✅ use event template if available, otherwise fallback
        if event.diploma_template:
            base_path = event.diploma_template.path
        else:
            base_path = os.path.join(settings.MEDIA_ROOT, "diploma_template.jpg")

        # calculate average scores for placements
        results = []
        for p in participations:
            scores = JudgeScore.objects.filter(participation=p)
            fields = ["technique", "composition", "image"]
            if p.style.name == "Show Dance":
                fields.append("show_value")

            total = Decimal(0)
            count = 0
            for f in fields:
                values = [getattr(s, f) for s in scores if getattr(s, f) is not None]
                if len(values) >= 3:
                    values = sorted(values)[1:-1]  # drop high + low
                if values:
                    total += sum(values)
                    count += len(values)

            avg_score = float(total / Decimal(count)) if count else 0.0
            results.append((p, avg_score))

        results.sort(key=lambda x: x[1], reverse=True)

        def draw_centered(draw, text, y, font, fill="black"):
            if not text:
                return
            W, H = img.size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            x = (W - text_w) / 2
            draw.text((x, y), text, font=font, fill=fill)

        category_text = " – ".join([style, group_type, age_group, difficulty])

        # ✅ cleanup old diplomas (DB + files) for this event & category
        old_diplomas = Diploma.objects.filter(event=event, category=category_text)
        for d in old_diplomas:
            if d.image and os.path.isfile(d.image.path):
                try:
                    os.remove(d.image.path)
                except Exception:
                    pass  # ignore errors if file already missing
        old_diplomas.delete()

        # generate diplomas
        for placement, (p, score) in enumerate(results, start=1):
            dancers = DancerParticipation.objects.filter(participation=p).select_related("dancer", "dancer__club")

            for dp in dancers:
                dancer = dp.dancer

                # ✅ use group_name if available and group is 4+
                if p.group_name and len(dancers) >= 4:
                    display_name = p.group_name
                else:
                    display_name = f"{dancer.first_name} {dancer.last_name}"

                choreo = p.choreography_name or ""
                club_name = dancer.club.club_name if dancer.club else "–"

                img = Image.open(base_path).convert("RGBA")
                draw = ImageDraw.Draw(img)
                W, H = img.size

                font_bold = ImageFont.truetype(
                    os.path.join(settings.BASE_DIR, "core/static/fonts/OpenSans-Bold.ttf"),
                    int(H * 0.05),
                )
                font_regular = ImageFont.truetype(
                    os.path.join(settings.BASE_DIR, "core/static/fonts/OpenSans-Regular.ttf"),
                    int(H * 0.035),
                )

                draw_centered(draw, f"{placement} PLACE", int(H * 0.62), font_bold)
                draw_centered(draw, category_text, int(H * 0.70), font_regular)
                draw_centered(draw, display_name, int(H * 0.77), font_regular)
                draw_centered(draw, club_name, int(H * 0.83), font_regular)  # ✅ club name
                draw_centered(draw, choreo, int(H * 0.89), font_regular)

                # ✅ ensure unique filename
                filename = f"diplomas/{event.id}_{p.id}_{dancer.id}_{placement}.png"
                full_path = os.path.join(settings.MEDIA_ROOT, filename)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                img.save(full_path)

                Diploma.objects.create(
                    event=event,
                    dancer=dancer,
                    category=category_text,
                    placement=placement,
                    image=filename,
                )

        messages.success(request, _("Diplomas generated successfully."))

        diplomas_qs = Diploma.objects.filter(
            event=event,
            category=category_text,
        )

        return render(request, "core/diploma_list.html", {
            "event": event,
            "diplomas": diplomas_qs,
        })

    return redirect("event_awards", event_id=event_id)



@staff_member_required
def diploma_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    diplomas = Diploma.objects.filter(event=event)

    # filter diplomas if category query param exists
    category_str = request.GET.get("category")
    if category_str:
        style, group_type, age_group, difficulty = category_str.split("|")
        diplomas = diplomas.filter(
            category=" – ".join([style.strip(), group_type.strip(), age_group.strip(), difficulty.strip()])
        )

    diplomas = diplomas.select_related("dancer").order_by("category", "placement")
    return render(
        request,
        "core/diploma_list.html",
        {"event": event, "diplomas": diplomas, "category": category_str},
    )


@login_required
def category_results(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    participations = (
        Participation.objects.filter(event=event)
        .select_related("style")
        .order_by("group_display_order", "display_order", "id")
    )

    # Group participations by category key
    grouped = defaultdict(list)
    for p in participations:
        group_key = (p.style.name, p.group_type, p.age_group, p.difficulty)
        grouped[group_key].append(p)

    results_by_category = {}
    for group_key, entries in grouped.items():
        ranked_entries = []
        for entry in entries:
            avg_score = JudgeScore.objects.filter(participation=entry).aggregate(
                avg=Avg("score")
            )["avg"]
            if avg_score is not None:
                ranked_entries.append((entry, round(avg_score, 2)))
        # Sort high to low
        ranked_entries.sort(key=lambda x: x[1], reverse=True)
        results_by_category[group_key] = ranked_entries

    context = {
        "event": event,
        "results_by_category": results_by_category,
    }
    return render(request, "core/event_awards.html", context)

@staff_member_required
@require_POST
def publish_event_results(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.results_published = True
    event.save()
    return redirect("event_awards", event_id=event.id)  # ✅ Redirect back to awards

@staff_member_required
@require_POST
def publish_awards(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.results_published = not event.results_published
    event.save()
    return redirect("event_awards", event_id=event.id)

@login_required
def participation_scores(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id)
    event = participation.event

    dancers = Dancer.objects.filter(dancerparticipation__participation=participation).select_related("club")
    club = dancers[0].club if dancers else None

    judge_scores = list(JudgeScore.objects.filter(participation=participation).select_related("judge"))

    criterion_fields = ["technique", "composition", "image"]
    if participation.style.name == "Show Dance":
        criterion_fields.append("show_value")

    discarded_ids = {f: set() for f in criterion_fields}
    for f in criterion_fields:
        vals = sorted([js for js in judge_scores if getattr(js, f) is not None], key=lambda js: getattr(js, f))
        if len(vals) > 2:
            discarded_ids[f].add(vals[0].id)
            discarded_ids[f].add(vals[-1].id)

    total_points = 0
    total_counts = 0
    for f in criterion_fields:
        vals = [getattr(js, f) for js in judge_scores if getattr(js, f) is not None and js.id not in discarded_ids[f]]
        total_points += sum(vals)
        total_counts += len(vals)

    final_score = round(total_points / total_counts, 2) if total_counts else 0

    # NEW: remember which category index we came from
    group_index = request.GET.get("group", 0)

    return render(request, "core/participation_scores.html", {
        "event": event,
        "participation": participation,
        "dancers": dancers,
        "club": club,
        "judge_scores": judge_scores,
        "discarded_ids": discarded_ids,
        "final_score": final_score,
        "group_index": group_index,
    })
