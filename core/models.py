from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class DanceClub(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="club")
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
    start_list_published = models.BooleanField(default=False, verbose_name=_("Is Start List Published"))
    results_published = models.BooleanField(default=False, verbose_name=_("Results Published"))
    discard_extreme_scores = models.BooleanField(
        default=True,
        verbose_name=_("Discard Highest/Lowest Judge Scores"),
    )
    allow_improv_challenge = models.BooleanField(default=False, verbose_name=_("Enable Improv Challenge"))
    start_time = models.TimeField(null=True, blank=True, verbose_name=_("Start Time"))
    notice_image = models.ImageField(
        upload_to="event_posters/",
        blank=True,
        null=True,
        verbose_name=_("Event Poster / Notice"),
    )
    diploma_template = models.ImageField(
        upload_to="diploma_templates/",
        null=True,
        blank=True,
        verbose_name=_("Diploma Template"),
    )
    organizer = models.ForeignKey(
        DanceClub,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_events",
        verbose_name=_("Organizer"),
    )
    allow_registrations = models.BooleanField(default=False)

    # NEW fields
    registration_start = models.DateField(null=True, blank=True, verbose_name=_("Registration Start Date"))
    registration_end = models.DateField(null=True, blank=True, verbose_name=_("Registration End Date"))
    music_end = models.DateField(null=True, blank=True, verbose_name=_("Music Upload End Date"))

    @property
    def registration_open(self):
        """Check if today is within registration period"""
        today = timezone.now().date()
        return (self.registration_start is None or today >= self.registration_start) and \
               (self.registration_end is None or today <= self.registration_end)

    @property
    def music_open(self):
        """Check if today is within music upload period"""
        today = timezone.now().date()
        if self.music_end:
            return (self.registration_start is None or today >= self.registration_start) and today <= self.music_end
        # if no music_end set, allow until event date
        return (self.registration_start is None or today >= self.registration_start) and today <= self.date

    def __str__(self):
        return f"{self.name} - {self.city} ({self.date})"

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["date"]


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
        ('Mixed Age', _("Mixed Age")),
        ('Mini Improv Challenge', _("Mini Improv Challenge (up to 10)")),
        ('Improv Challenge 11+', _("Improv Challenge 11+")),
    ]

    DIFFICULTY_CHOICES = [
        ('', _("No difficulty")),
        ('A', _("Advanced")),
        ('B', _("Beginner/Basic")),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("Event"))
    group_type = models.CharField(max_length=20, choices=CHOREO_TYPE_CHOICES, verbose_name=_("Group Type"))
    age_group = models.CharField(max_length=30, choices=AGE_GROUP_CHOICES, verbose_name=_("Age Group"))
    style = models.ForeignKey("StyleCategory", on_delete=models.CASCADE, verbose_name=_("Style"))
    choreographer_name = models.CharField(max_length=255, blank=True, verbose_name=_("Choreographer Name"))
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES, blank=True, default="", verbose_name=_("Difficulty"))
    start_number = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Start Number"))
    display_order = models.PositiveIntegerField(null=True, blank=True, default=None, verbose_name=_("Display Order"))
    choreography_name = models.CharField(max_length=255, blank=True, default=_("Untitled"), verbose_name=_("Choreography Name"))
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


class ImprovChallengeConfig(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="improv_config")
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name=_("Improv Challenge Duration (minutes)"))
    current_round_number = models.PositiveIntegerField(default=1, verbose_name=_("Current Round"))

    class Meta:
        verbose_name = _("Improv Challenge Config")
        verbose_name_plural = _("Improv Challenge Configs")

    def __str__(self):
        return f"{self.event} improv challenge"


class ImprovChallengeRound(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="improv_rounds")
    round_number = models.PositiveIntegerField(verbose_name=_("Round Number"))
    target_count = models.PositiveIntegerField(verbose_name=_("Participants to Advance"))
    is_final = models.BooleanField(default=False, verbose_name=_("Final Round"))
    finalized = models.BooleanField(default=False, verbose_name=_("Finalized"))

    class Meta:
        unique_together = ("event", "round_number")
        ordering = ["round_number"]
        verbose_name = _("Improv Challenge Round")
        verbose_name_plural = _("Improv Challenge Rounds")

    def __str__(self):
        return f"{self.event} - Round {self.round_number}"


class ImprovJudgeSelection(models.Model):
    round = models.ForeignKey(ImprovChallengeRound, on_delete=models.CASCADE, related_name="judge_selections")
    judge = models.ForeignKey(User, on_delete=models.CASCADE, related_name="improv_selections")
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name="improv_selections")
    rank = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Rank"))

    class Meta:
        unique_together = ("round", "judge", "participation")
        verbose_name = _("Improv Judge Selection")
        verbose_name_plural = _("Improv Judge Selections")

    def __str__(self):
        return f"{self.judge} - {self.round} - {self.participation}"


class ImprovRoundQualifier(models.Model):
    round = models.ForeignKey(ImprovChallengeRound, on_delete=models.CASCADE, related_name="qualifiers")
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name="improv_qualifications")

    class Meta:
        unique_together = ("round", "participation")
        verbose_name = _("Improv Round Qualifier")
        verbose_name_plural = _("Improv Round Qualifiers")

    def __str__(self):
        return f"{self.participation} qualified from {self.round}"


class Diploma(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("Event"))
    dancer = models.ForeignKey(Dancer, on_delete=models.CASCADE, verbose_name=_("Dancer"))
    category = models.CharField(max_length=255, verbose_name=_("Category"))
    placement = models.PositiveIntegerField(verbose_name=_("Placement"))
    image = models.ImageField(upload_to="diplomas/", verbose_name=_("Diploma Image"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Diploma")
        verbose_name_plural = _("Diplomas")

    def __str__(self):
        return f"{self.dancer} – {self.category} – Place {self.placement}"
    
class StartListSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="slots")
    title = models.CharField(max_length=255, verbose_name=_("Heading"))
    duration_minutes = models.PositiveIntegerField(verbose_name=_("Duration (minutes)"))
    display_order = models.PositiveIntegerField(default=0)
    is_ceremony = models.BooleanField(default=False)
    age_group = models.CharField(
        max_length=30,
        choices=Participation.AGE_GROUP_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Age Group (optional)"),
    )

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.title} ({self.age_group}, {self.duration_minutes} min)"
