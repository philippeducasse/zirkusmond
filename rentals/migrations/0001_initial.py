import markdownx.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='RentalObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', markdownx.models.MarkdownxField()),
                ('image', models.ImageField(upload_to='')),
                ('link', models.CharField(blank=True, max_length=255)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
