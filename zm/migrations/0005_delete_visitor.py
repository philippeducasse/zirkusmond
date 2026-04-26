from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zm', '0004_rentalobject'),
    ]

    operations = [
        migrations.DeleteModel(name='Visitor'),
    ]