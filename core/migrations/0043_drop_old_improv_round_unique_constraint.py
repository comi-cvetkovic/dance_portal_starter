from django.db import migrations


def drop_old_improv_round_unique_constraint(apps, schema_editor):
    table_name = "core_improvchallengeround"
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, table_name)

    old_columns = ["event_id", "round_number"]
    with connection.cursor() as cursor:
        for constraint_name, details in constraints.items():
            if details.get("unique") and details.get("columns") == old_columns:
                quoted_table = schema_editor.quote_name(table_name)
                quoted_constraint = schema_editor.quote_name(constraint_name)
                cursor.execute(f"ALTER TABLE {quoted_table} DROP CONSTRAINT {quoted_constraint}")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0042_split_improv_challenge_age_groups"),
    ]

    operations = [
        migrations.RunPython(
            drop_old_improv_round_unique_constraint,
            migrations.RunPython.noop,
        ),
    ]
