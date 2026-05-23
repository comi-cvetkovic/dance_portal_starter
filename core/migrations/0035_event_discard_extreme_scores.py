from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0034_event_music_end_event_registration_end_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="discard_extreme_scores",
            field=models.BooleanField(
                default=True,
                verbose_name="Discard Highest/Lowest Judge Scores",
            ),
        ),
    ]

