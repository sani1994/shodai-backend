# Generated by Django 2.2.5 on 2019-09-26 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0006_auto_20190925_1424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='token',
        ),
    ]
