# Generated by Django 3.0.2 on 2020-01-13 01:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matchchatmessage',
            old_name='username',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='matchsubscription',
            old_name='username',
            new_name='user',
        ),
        migrations.AlterUniqueTogether(
            name='matchsubscription',
            unique_together={('match', 'user')},
        ),
    ]
