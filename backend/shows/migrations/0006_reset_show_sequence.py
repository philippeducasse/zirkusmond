from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shows", "0005_alter_show_seo_image_crop"),
    ]

    operations = [
        migrations.RunSQL(
            sql="SELECT setval(pg_get_serial_sequence('shows_show', 'id'), MAX(id)) FROM shows_show;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
