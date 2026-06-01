from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0035_event_discard_extreme_scores"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventregistration",
            name="age_group",
            field=models.CharField(
                choices=[
                    ("Baby", "Baby (5-6)"),
                    ("Mini Kids", "Mini Kids (7-8)"),
                    ("Kids", "Kids (9-11)"),
                    ("Teen", "Teen (12-14)"),
                    ("Youth", "Youth (15-17)"),
                    ("Adult", "Adult (18 and up)"),
                    ("Mixed Age", "Mixed Age"),
                ],
                max_length=50,
                verbose_name="Age Group",
            ),
        ),
        migrations.AlterField(
            model_name="participation",
            name="age_group",
            field=models.CharField(
                choices=[
                    ("Baby", "Baby (5-6)"),
                    ("Mini Kids", "Mini Kids (7-8)"),
                    ("Kids", "Kids (9-11)"),
                    ("Teen", "Teen (12-14)"),
                    ("Youth", "Youth (15-17)"),
                    ("Adult", "Adult (18 and up)"),
                    ("Mixed Age", "Mixed Age"),
                ],
                max_length=20,
                verbose_name="Age Group",
            ),
        ),
        migrations.AlterField(
            model_name="startlistslot",
            name="age_group",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Baby", "Baby (5-6)"),
                    ("Mini Kids", "Mini Kids (7-8)"),
                    ("Kids", "Kids (9-11)"),
                    ("Teen", "Teen (12-14)"),
                    ("Youth", "Youth (15-17)"),
                    ("Adult", "Adult (18 and up)"),
                    ("Mixed Age", "Mixed Age"),
                ],
                max_length=20,
                null=True,
                verbose_name="Age Group (optional)",
            ),
        ),
    ]

