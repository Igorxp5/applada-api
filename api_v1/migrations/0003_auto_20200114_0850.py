# Generated by Django 3.0.2 on 2020-01-14 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0002_auto_20200112_2221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='limit_participants',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
