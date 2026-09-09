from django.db import migrations, models
import django.utils.translation


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0037_event_organizer"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="allow_improv_challenge",
            field=models.BooleanField(
                default=False,
                verbose_name=django.utils.translation.gettext_lazy("Enable Improv Challenge"),
            ),
        ),
        migrations.AlterField(
            model_name="participation",
            name="age_group",
            field=models.CharField(
                choices=[
                    ("Baby", django.utils.translation.gettext_lazy("Baby (5-6)")),
                    ("Mini Kids", django.utils.translation.gettext_lazy("Mini Kids (7-8)")),
                    ("Kids", django.utils.translation.gettext_lazy("Kids (9-11)")),
                    ("Teen", django.utils.translation.gettext_lazy("Teen (12-14)")),
                    ("Youth", django.utils.translation.gettext_lazy("Youth (15-17)")),
                    ("Adult", django.utils.translation.gettext_lazy("Adult (18 and up)")),
                    ("Mixed Age", django.utils.translation.gettext_lazy("Mixed Age")),
                    ("Mini Improv Challenge", django.utils.translation.gettext_lazy("Mini Improv Challenge (up to 10)")),
                    ("Improv Challenge 11+", django.utils.translation.gettext_lazy("Improv Challenge 11+")),
                ],
                max_length=30,
                verbose_name=django.utils.translation.gettext_lazy("Age Group"),
            ),
        ),
        migrations.AlterField(
            model_name="eventregistration",
            name="age_group",
            field=models.CharField(
                choices=[
                    ("Baby", django.utils.translation.gettext_lazy("Baby (5-6)")),
                    ("Mini Kids", django.utils.translation.gettext_lazy("Mini Kids (7-8)")),
                    ("Kids", django.utils.translation.gettext_lazy("Kids (9-11)")),
                    ("Teen", django.utils.translation.gettext_lazy("Teen (12-14)")),
                    ("Youth", django.utils.translation.gettext_lazy("Youth (15-17)")),
                    ("Adult", django.utils.translation.gettext_lazy("Adult (18 and up)")),
                    ("Mixed Age", django.utils.translation.gettext_lazy("Mixed Age")),
                    ("Mini Improv Challenge", django.utils.translation.gettext_lazy("Mini Improv Challenge (up to 10)")),
                    ("Improv Challenge 11+", django.utils.translation.gettext_lazy("Improv Challenge 11+")),
                ],
                max_length=50,
                verbose_name=django.utils.translation.gettext_lazy("Age Group"),
            ),
        ),
        migrations.AlterField(
            model_name="participation",
            name="choreographer_name",
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name=django.utils.translation.gettext_lazy("Choreographer Name"),
            ),
        ),
        migrations.AlterField(
            model_name="participation",
            name="choreography_name",
            field=models.CharField(
                blank=True,
                default=django.utils.translation.gettext_lazy("Untitled"),
                max_length=255,
                verbose_name=django.utils.translation.gettext_lazy("Choreography Name"),
            ),
        ),
        migrations.AlterField(
            model_name="participation",
            name="difficulty",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", django.utils.translation.gettext_lazy("No difficulty")),
                    ("A", django.utils.translation.gettext_lazy("Advanced")),
                    ("B", django.utils.translation.gettext_lazy("Beginner/Basic")),
                ],
                default="",
                max_length=1,
                verbose_name=django.utils.translation.gettext_lazy("Difficulty"),
            ),
        ),
    ]
