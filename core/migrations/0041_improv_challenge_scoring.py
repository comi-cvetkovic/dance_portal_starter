from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.translation


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0040_participation_start_number"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ImprovChallengeConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("duration_minutes", models.PositiveIntegerField(default=0, verbose_name=django.utils.translation.gettext_lazy("Improv Challenge Duration (minutes)"))),
                ("current_round_number", models.PositiveIntegerField(default=1, verbose_name=django.utils.translation.gettext_lazy("Current Round"))),
                ("event", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="improv_config", to="core.event")),
            ],
            options={
                "verbose_name": django.utils.translation.gettext_lazy("Improv Challenge Config"),
                "verbose_name_plural": django.utils.translation.gettext_lazy("Improv Challenge Configs"),
            },
        ),
        migrations.CreateModel(
            name="ImprovChallengeRound",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("round_number", models.PositiveIntegerField(verbose_name=django.utils.translation.gettext_lazy("Round Number"))),
                ("target_count", models.PositiveIntegerField(verbose_name=django.utils.translation.gettext_lazy("Participants to Advance"))),
                ("is_final", models.BooleanField(default=False, verbose_name=django.utils.translation.gettext_lazy("Final Round"))),
                ("finalized", models.BooleanField(default=False, verbose_name=django.utils.translation.gettext_lazy("Finalized"))),
                ("event", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="improv_rounds", to="core.event")),
            ],
            options={
                "verbose_name": django.utils.translation.gettext_lazy("Improv Challenge Round"),
                "verbose_name_plural": django.utils.translation.gettext_lazy("Improv Challenge Rounds"),
                "ordering": ["round_number"],
                "unique_together": {("event", "round_number")},
            },
        ),
        migrations.CreateModel(
            name="ImprovJudgeSelection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rank", models.PositiveIntegerField(blank=True, null=True, verbose_name=django.utils.translation.gettext_lazy("Rank"))),
                ("judge", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="improv_selections", to=settings.AUTH_USER_MODEL)),
                ("participation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="improv_selections", to="core.participation")),
                ("round", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="judge_selections", to="core.improvchallengeround")),
            ],
            options={
                "verbose_name": django.utils.translation.gettext_lazy("Improv Judge Selection"),
                "verbose_name_plural": django.utils.translation.gettext_lazy("Improv Judge Selections"),
                "unique_together": {("round", "judge", "participation")},
            },
        ),
        migrations.CreateModel(
            name="ImprovRoundQualifier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("participation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="improv_qualifications", to="core.participation")),
                ("round", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="qualifiers", to="core.improvchallengeround")),
            ],
            options={
                "verbose_name": django.utils.translation.gettext_lazy("Improv Round Qualifier"),
                "verbose_name_plural": django.utils.translation.gettext_lazy("Improv Round Qualifiers"),
                "unique_together": {("round", "participation")},
            },
        ),
    ]
