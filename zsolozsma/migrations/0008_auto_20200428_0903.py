# Generated by Django 3.0.5 on 2020-04-28 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zsolozsma', '0007_broadcast'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='youtube_channel',
            field=models.CharField(blank=True, max_length=24, verbose_name='YouTube csatorna ID'),
        ),
    ]
