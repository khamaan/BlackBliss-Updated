# Generated by Django 4.2.2 on 2023-07-10 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_reviewrating_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewrating',
            name='userprofile',
        ),
    ]
