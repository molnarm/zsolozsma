# Generated by Django 3.0.5 on 2020-11-12 08:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zsolozsma', '0018_auto_20200909_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='Diocese',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Név')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='URL részlet')),
            ],
            options={
                'verbose_name': 'Egyházmegye',
                'verbose_name_plural': 'Egyházmegyék',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Név')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='URL részlet')),
                ('diocese', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.Diocese', verbose_name='Egyházmegye')),
            ],
            options={
                'verbose_name': 'Település',
                'verbose_name_plural': 'Települések',
            },
        ),
        migrations.AddField(
            model_name='location',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.City', verbose_name='Település'),
        ),
    ]