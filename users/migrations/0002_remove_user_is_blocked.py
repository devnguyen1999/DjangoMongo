# Generated by Django 3.0.5 on 2021-07-13 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_blocked',
        ),
    ]
