from django import forms
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.utils.translation import gettext_lazy as _
from .models import Dancer, Event, Participation, DanceClub, StyleCategory, JudgeScore
from mutagen.mp3 import MP3


class DancerForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_("Date of Birth")
    )

    class Meta:
        model = Dancer
        fields = ['first_name', 'last_name', 'date_of_birth']
        labels = {
            'first_name': _("First Name"),
            'last_name': _("Last Name"),
        }


class DanceClubRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True, label=_("Email"))
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label=_("Password (leave blank to keep unchanged)")
    )
    country = CountryField().formfield(widget=CountrySelectWidget(), label=_("Country"))

    class Meta:
        model = DanceClub
        fields = [
            'club_name',
            'country',
            'city',
            'phone_number',
            'representative_name',
            'email',
            'password',
        ]
        labels = {
            'club_name': _("Club Name"),
            'city': _("City"),
            'phone_number': _("Phone Number"),
            'representative_name': _("Representative Name"),
        }

    def clean_email(self):
        """Make sure the email (used as login) is unique, except for the current club."""
        email = self.cleaned_data['email']
        qs = User.objects.filter(username=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError(_("A club with this email already exists."))
        return email

    def save(self, commit=True):
        dance_club = super().save(commit=False)
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if dance_club.pk:  # Editing existing club
            user = dance_club.user
            if email and user.email != email:
                user.email = email
                user.username = email
            if password:
                user.set_password(password)
                dance_club.raw_password = password
        else:  # Creating new club
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            dance_club.user = user
            dance_club.raw_password = password

        if commit:
            user.save()
            dance_club.save()

        return dance_club


class EventForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_("Date")
    )

    start_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label=_("Start Time")
    )

    class Meta:
        model = Event
        fields = ['name', 'location', 'city', 'date', 'start_time', 'notice_image']
        labels = {
            'name': _("Event Name"),
            'location': _("Location"),
            'city': _("City"),
            'date': _("Date"),
            'notice_image': _("Event Poster / Notice (optional)"),
        }


class ParticipationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        club = kwargs.pop('club', None)
        event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)

        if club:
            self.fields['dancer'].queryset = Dancer.objects.filter(club=club)
        if event:
            self.fields['style'].queryset = StyleCategory.objects.filter(event=event)

        self.fields['dancer'].widget.attrs.update({'id': 'id_dancer'})

    class Meta:
        model = Participation
        fields = ['style', 'difficulty', 'age_group', 'group_type', 'choreographer_name']
        labels = {
            'style': _("Style"),
            'difficulty': _("Difficulty"),
            'age_group': _("Age Group"),
            'group_type': _("Group Type"),
            'choreographer_name': _("Choreographer Name"),
        }


class GroupParticipationForm(forms.Form):
    dancers = forms.ModelMultipleChoiceField(
        queryset=Dancer.objects.none(),
        widget=forms.SelectMultiple(attrs={"id": "id_dancers"}),
        label=_("Dancers")
    )
    style = forms.ModelChoiceField(queryset=StyleCategory.objects.none(), label=_("Style"))
    group_type = forms.ChoiceField(choices=Participation.CHOREO_TYPE_CHOICES, label=_("Group Type"))
    age_group = forms.ChoiceField(
        choices=Participation.AGE_GROUP_CHOICES,
        disabled=True,
        required=False,
        label=_("Age Group")
    )
    difficulty = forms.ChoiceField(choices=Participation.DIFFICULTY_CHOICES, label=_("Difficulty"))
    choreographer_name = forms.CharField(max_length=255, label=_("Choreographer Name"))
    choreography_name = forms.CharField(max_length=255, required=True, label=_("Choreography Name"))
    group_name = forms.CharField(
        max_length=255,
        required=False,
        label=_("Group Name"),
        widget=forms.TextInput(attrs={'placeholder': _("Enter group name (for groups of 4+)"), 'id': 'id_group_name'})
    )
    music_file = forms.FileField(required=True, label=_("Music File"))

    def __init__(self, *args, **kwargs):
        club = kwargs.pop('club', None)
        event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)

        if club:
            self.fields['dancers'].queryset = Dancer.objects.filter(club=club)
        if event:
            self.fields['style'].queryset = StyleCategory.objects.filter(event=event)

    def clean_dancers(self):
        dancers = self.cleaned_data.get("dancers")

        # Drop any empty placeholder values
        if dancers:
            dancers = [d for d in dancers if d]
        return dancers

    def clean(self):
        cleaned_data = super().clean()
        dancers = cleaned_data.get("dancers")
        group_type = cleaned_data.get("group_type")

        # Force to list and drop blanks
        dancers = list(dancers) if dancers else []
        dancers = [d for d in dancers if getattr(d, "id", None)]  # drop None/empty
        cleaned_data["dancers"] = dancers

        limits = {
            'Solo': (1, 1),
            'Duo': (2, 2),
            'Trio': (3, 3),
            'Group': (4, 9),
            'Formation': (10, 29),
            'Production': (30, 200),
        }

        if group_type in limits:
            min_required, max_required = limits[group_type]
            if not (min_required <= len(dancers) <= max_required):
                raise forms.ValidationError(
                    f"{group_type} requires between {min_required} and {max_required} dancers. "
                    f"You selected {len(dancers)}."
                )

        if group_type in ['Group', 'Formation', 'Production'] and not cleaned_data.get('group_name'):
            raise forms.ValidationError("Group name is required for groups of 4 or more dancers.")

        return cleaned_data


    def clean_music_file(self):
        music_file = self.cleaned_data.get("music_file")
        group_type = self.cleaned_data.get("group_type")

        if not music_file:
            return music_file

        if not music_file.name.lower().endswith(".mp3"):
            raise forms.ValidationError(_("Only MP3 files are supported."))

        try:
            music_file.seek(0)
            audio = MP3(music_file.file)
            duration = audio.info.length
        except Exception:
            raise forms.ValidationError(_("Failed to process the uploaded MP3 file."))

        limits = {
            "Solo": 135,
            "Duo": 135,
            "Trio": 135,
            "Group": 180,
            "Formation": 240,
        }

        limit = limits.get(group_type)
        if limit and duration > limit:
            raise forms.ValidationError(
                _(f"File too long for {group_type}. Max is {limit // 60}:{limit % 60:02d}, "
                  f"but your file is {int(duration // 60)}:{int(duration % 60):02d}.")
            )

        return music_file


class SingleJudgeForm(forms.Form):
    first_name = forms.CharField(max_length=50, label=_("First Name"))
    last_name = forms.CharField(max_length=50, label=_("Last Name"))


JudgeCreationFormSet = forms.formset_factory(SingleJudgeForm, extra=3, min_num=1, validate_min=True)


class JudgeScoreForm(forms.ModelForm):
    class Meta:
        model = JudgeScore
        fields = []  # No direct single field now

