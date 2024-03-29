# Generated by Django 3.0.2 on 2020-01-19 15:40

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='match',
            name='lon',
        ),
        migrations.AddField(
            model_name='match',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default=None, srid=4326, verbose_name='location'),
            preserve_default=False,
        ),
    ]
