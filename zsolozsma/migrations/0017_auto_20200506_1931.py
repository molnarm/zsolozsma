# Generated by Django 3.0.5 on 2020-05-06 17:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zsolozsma', '0016_auto_20200506_1925'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='broadcast',
            name='event',
        ),
        migrations.RemoveField(
            model_name='event',
            name='hash',
        ),
        migrations.AddField(
            model_name='broadcast',
            name='schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.EventSchedule', verbose_name='Esemény időpont'),
        ),
        migrations.AddField(
            model_name='eventschedule',
            name='hash',
            field=models.CharField(max_length=8, null=True, unique=True, verbose_name='URL hash'),
        ),
    ]
