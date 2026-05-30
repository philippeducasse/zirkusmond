from django.db import migrations


def reset_sequence(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(
            "SELECT setval(pg_get_serial_sequence('shows_show', 'id'), MAX(id)) FROM shows_show;"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("shows", "0005_alter_show_seo_image_crop"),
    ]

    operations = [
        migrations.RunPython(reset_sequence, migrations.RunPython.noop),
    ]
