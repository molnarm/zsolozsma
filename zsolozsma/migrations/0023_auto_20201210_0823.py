# Generated by Django 3.0.5 on 2020-12-10 07:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zsolozsma', '0022_auto_20201201_1455'),
    ]

    operations = [
        migrations.CreateModel(
            name='Denomination',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Név')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='URL részlet')),
            ],
            options={
                'verbose_name': 'Felekezet',
                'verbose_name_plural': 'Felekezetek',
            },
        ),
        migrations.RemoveField(
            model_name='city',
            name='diocese',
        ),
        migrations.AlterField(
            model_name='broadcast',
            name='video_youtube_channel',
            field=models.URLField(blank=True, max_length=24, null=True, verbose_name='Videó YouTube csatorna'),
        ),
        migrations.DeleteModel(
            name='Diocese',
        ),
        migrations.AddField(
            model_name='liturgy',
            name='denomination',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.Denomination', verbose_name='Felekezet'),
        ),
    ]
