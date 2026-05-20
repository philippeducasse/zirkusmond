from django.db import migrations


def copy_newsletter_emails(apps, schema_editor):
    NewsletterEmail = apps.get_model('events', 'NewsletterEmail')
    NewsletterRegistration = apps.get_model('newsletter', 'NewsletterRegistration')

    existing = set(NewsletterRegistration.objects.values_list('email', flat=True))
    to_create = [
        NewsletterRegistration(email=obj.email)
        for obj in NewsletterEmail.objects.all()
        if obj.email not in existing
    ]
    NewsletterRegistration.objects.bulk_create(to_create)


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_guest_checked_in_guest_ticket_id'),
        ('newsletter', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_newsletter_emails, migrations.RunPython.noop),
        migrations.DeleteModel(name='NewsletterEmail'),
    ]
