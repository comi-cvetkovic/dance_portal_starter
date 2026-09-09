from django.db import migrations, models


def backfill_start_numbers(apps, schema_editor):
    Participation = apps.get_model("core", "Participation")
    Event = apps.get_model("core", "Event")

    for event in Event.objects.all().only("id"):
        entries = sorted(
            Participation.objects.filter(event_id=event.id),
            key=lambda participation: (
                participation.display_order if participation.display_order is not None else 999999,
                participation.id,
            ),
        )
        for offset, participation in enumerate(entries, start=101):
            if participation.start_number is None:
                participation.start_number = offset
                participation.save(update_fields=["start_number"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0039_alter_startlistslot_age_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="participation",
            name="start_number",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="Start Number",
            ),
        ),
        migrations.RunPython(backfill_start_numbers, migrations.RunPython.noop),
    ]
