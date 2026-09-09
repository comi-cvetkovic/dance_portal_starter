from django.db import migrations, models
import django.utils.translation


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0038_event_allow_improv_challenge_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="startlistslot",
            name="age_group",
            field=models.CharField(
                blank=True,
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
                null=True,
                verbose_name=django.utils.translation.gettext_lazy("Age Group (optional)"),
            ),
        ),
    ]
