from django.db import migrations, models
import django.utils.translation


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0041_improv_challenge_scoring"),
    ]

    operations = [
        migrations.AddField(
            model_name="improvchallengeconfig",
            name="challenge_duration_minutes",
            field=models.PositiveIntegerField(default=0, verbose_name=django.utils.translation.gettext_lazy("Improv Challenge 11+ Duration (minutes)")),
        ),
        migrations.AddField(
            model_name="improvchallengeconfig",
            name="current_age_group",
            field=models.CharField(blank=True, default="Mini Improv Challenge", max_length=30, verbose_name=django.utils.translation.gettext_lazy("Current Improv Age Group")),
        ),
        migrations.AddField(
            model_name="improvchallengeconfig",
            name="mini_duration_minutes",
            field=models.PositiveIntegerField(default=0, verbose_name=django.utils.translation.gettext_lazy("Mini Improv Challenge Duration (minutes)")),
        ),
        migrations.AddField(
            model_name="improvchallengeround",
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
                default="Mini Improv Challenge",
                max_length=30,
                verbose_name=django.utils.translation.gettext_lazy("Age Group"),
            ),
        ),
        migrations.AlterUniqueTogether(
            name="improvchallengeround",
            unique_together={("event", "age_group", "round_number")},
        ),
    ]
