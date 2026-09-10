# Generated manually because the local environment does not have Django installed.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0043_drop_old_improv_round_unique_constraint"),
    ]

    operations = [
        migrations.CreateModel(
            name="CategoryRound",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("group_type", models.CharField(choices=[("Solo", "Solo"), ("Duo", "Duo"), ("Trio", "Trio"), ("Group", "Group (4-9)"), ("Formation", "Formation (10-29)"), ("Production", "Production (30+)")], max_length=20, verbose_name="Group Type")),
                ("age_group", models.CharField(choices=[("Baby", "Baby (5-6)"), ("Mini Kids", "Mini Kids (7-8)"), ("Kids", "Kids (9-11)"), ("Teen", "Teen (12-14)"), ("Youth", "Youth (15-17)"), ("Adult", "Adult (18 and up)"), ("Mixed Age", "Mixed Age"), ("Mini Improv Challenge", "Mini Improv Challenge (up to 10)"), ("Improv Challenge 11+", "Improv Challenge 11+")], max_length=30, verbose_name="Age Group")),
                ("difficulty", models.CharField(blank=True, choices=[("", "No difficulty"), ("A", "Advanced"), ("B", "Beginner/Basic")], default="", max_length=1, verbose_name="Difficulty")),
                ("round_number", models.PositiveIntegerField(verbose_name="Round Number")),
                ("target_count", models.PositiveIntegerField(verbose_name="Participants to Advance")),
                ("is_final", models.BooleanField(default=False, verbose_name="Final Round")),
                ("finalized", models.BooleanField(default=False, verbose_name="Finalized")),
                ("event", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="category_rounds", to="core.event")),
                ("style", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="category_rounds", to="core.stylecategory")),
            ],
            options={
                "verbose_name": "Category Round",
                "verbose_name_plural": "Category Rounds",
                "ordering": ["event", "style", "group_type", "age_group", "difficulty", "round_number"],
                "unique_together": {("event", "style", "group_type", "age_group", "difficulty", "round_number")},
            },
        ),
        migrations.CreateModel(
            name="CategoryRoundQualifier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("participation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="category_round_qualifications", to="core.participation")),
                ("round", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="qualifiers", to="core.categoryround")),
            ],
            options={
                "verbose_name": "Category Round Qualifier",
                "verbose_name_plural": "Category Round Qualifiers",
                "unique_together": {("round", "participation")},
            },
        ),
    ]
