# Generated by Django 3.0.5 on 2020-04-28 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zsolozsma', '0008_auto_20200428_0903'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcast',
            name='video_only',
            field=models.BooleanField(blank=True, default=True, verbose_name='Beágyazás csak maga a videó'),
        ),
    ]
