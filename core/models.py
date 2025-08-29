from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _

class DanceClub(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    raw_password = models.CharField(
        max_length=128, blank=True, null=True,
        verbose_name=_("Raw Password")  # Store plaintext password (not secure!)
    )
    club_name = models.CharField(max_length=255, verbose_name=_("Club Name"))
    country = CountryField(verbose_name=_("Country"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"))
    representative_name = models.CharField(max_length=255, verbose_name=_("Representative Name"))
    confirmed = models.BooleanField(default=False, verbose_name=_("Confirmed"))

    def __str__(self):
        return self.club_name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_club_user')
        ]
        verbose_name = _("Dance Club")
        verbose_name_plural = _("Dance Clubs")


class Dancer(models.Model):
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    date_of_birth = models.DateField(verbose_name=_("Date of Birth"))
    club = models.ForeignKey(
        DanceClub, on_delete=models.CASCADE, related_name='dancers',
        verbose_name=_("Club")
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("Dancer")
        verbose_name_plural = _("Dancers")


class Event(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Event Name"))
    location = models.CharField(max_length=100, verbose_name=_("Location"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    date = models.DateField(verbose_name=_("Date"))
    is_published = models.BooleanField(default=False, verbose_name=_("Is Published"))
    results_published = models.BooleanField(default=False, verbose_name=_("Results Published"))
    start_time = models.TimeField(null=True, blank=True, verbose_name=_("Start Time"))
    notice_image = models.ImageField(
        upload_to='event_posters/',
        blank=True,
        null=True,
        verbose_name="Event Poster / Notice"
    )

    allow_registrations = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.city} ({self.date})"

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")


class Participation(models.Model):
    CHOREO_TYPE_CHOICES = [
        ('Solo', _("Solo")),
        ('Duo', _("Duo")),
        ('Trio', _("Trio")),
        ('Group', _("Group (4-9)")),
        ('Formation', _("Formation (10-29)")),
        ('Production', _("Production (30+)")),
    ]

    AGE_GROUP_CHOICES = [
        ('Baby', _("Baby (5-6)")),
        ('Mini Kids', _("Mini Kids (7-8)")),
        ('Kids', _("Kids (9-11)")),
        ('Teen', _("Teen (12-14)")),
        ('Youth', _("Youth (15-17)")),
        ('Adult', _("Adult (18 and up)")),
    ]

    DIFFICULTY_CHOICES = [
        ('A', _("Advanced")),
        ('B', _("Beginner/Basic")),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("Event"))
    group_type = models.CharField(max_length=20, choices=CHOREO_TYPE_CHOICES, verbose_name=_("Group Type"))
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES, verbose_name=_("Age Group"))
    style = models.ForeignKey("StyleCategory", on_delete=models.CASCADE, verbose_name=_("Style"))
    choreographer_name = models.CharField(max_length=255, verbose_name=_("Choreographer Name"))
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES, verbose_name=_("Difficulty"))
    display_order = models.PositiveIntegerField(null=True, blank=True, default=None, verbose_name=_("Display Order"))
    choreography_name = models.CharField(max_length=255, default=_("Untitled"), verbose_name=_("Choreography Name"))
    group_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Group Name"))
    group_display_order = models.PositiveIntegerField(null=True, blank=True, default=0, verbose_name=_("Group Display Order"))
    music_file = models.FileField(upload_to='music_uploads/', null=True, blank=True, verbose_name=_("Music File"))

    def __str__(self):
        return f"{self.group_type} - {self.style} ({self.age_group})"

    class Meta:
        verbose_name = _("Participation")
        verbose_name_plural = _("Participations")


class EventRegistration(models.Model):
    dancer = models.ForeignKey(Dancer, on_delete=models.CASCADE, verbose_name=_("Dancer"))
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("Event"))
    style_category = models.ForeignKey("StyleCategory", on_delete=models.CASCADE, verbose_name=_("Style Category"))
    group_type = models.CharField(max_length=50, choices=Participation.CHOREO_TYPE_CHOICES, verbose_name=_("Group Type"))
    age_group = models.CharField(max_length=50, choices=Participation.AGE_GROUP_CHOICES, verbose_name=_("Age Group"))

    def __str__(self):
        return f"{self.dancer} - {self.event} ({self.style_category})"

    class Meta:
        verbose_name = _("Event Registration")
        verbose_name_plural = _("Event Registrations")


class StyleCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='style_categories', verbose_name=_("Event"))

    class Meta:
        unique_together = ('event', 'name')
        verbose_name = _("Style Category")
        verbose_name_plural = _("Style Categories")

    def __str__(self):
        return self.name


class DancerParticipation(models.Model):
    participation = models.ForeignKey(
        Participation, on_delete=models.CASCADE, related_name='dancer_links',
        verbose_name=_("Participation")
    )
    dancer = models.ForeignKey('Dancer', on_delete=models.CASCADE, verbose_name=_("Dancer"))

    def __str__(self):
        return f"{self.dancer} in {self.participation}"

    class Meta:
        verbose_name = _("Dancer Participation")
        verbose_name_plural = _("Dancer Participations")


class EventPlaybackState(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, verbose_name=_("Event"))
    current_highlight_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Current Highlight Key"))

    class Meta:
        verbose_name = _("Event Playback State")
        verbose_name_plural = _("Event Playback States")


class JudgeScore(models.Model):
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE, verbose_name=_("Participation"))
    judge = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Judge"))

    technique = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    composition = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    image = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    show_value = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # only for Show Dance

    class Meta:
        unique_together = ('participation', 'judge')
        verbose_name = _("Judge Score")
        verbose_name_plural = _("Judge Scores")