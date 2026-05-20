from django.db import migrations, models
from django.db.utils import IntegrityError

def seed_sitestats(apps, schema_editor):
    SiteStats = apps.get_model('events', 'SiteStats')
    db_alias = schema_editor.connection.alias
    try:
        SiteStats.objects.using(db_alias).get_or_create(pk=1, defaults={"deleted_visitors": 0})
    except IntegrityError:
        # If someone already inserted one in parallel or via fixtures, ignore.
        pass

def unseed_sitestats(apps, schema_editor):
    SiteStats = apps.get_model('events', 'SiteStats')
    db_alias = schema_editor.connection.alias
    # Only remove the seeded one; leave others alone if they exist
    SiteStats.objects.using(db_alias).filter(pk=1).delete()

class Migration(migrations.Migration):

    dependencies = [
        ("events", "0003_remove_event_reservation_price_and_more"),
    ]


    operations = [
        migrations.CreateModel(
            name='SiteStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_visitors', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.RunPython(seed_sitestats, unseed_sitestats),
    ]
