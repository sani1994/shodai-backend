# Generated by Django 2.2.5 on 2019-10-16 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0010_auto_20191016_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]