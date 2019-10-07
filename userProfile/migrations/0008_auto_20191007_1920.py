# Generated by Django 2.2.5 on 2019-10-07 19:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0007_remove_userprofile_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otp',
            name='forgot',
        ),
        migrations.RemoveField(
            model_name='otp',
            name='forgot_logged',
        ),
        migrations.RemoveField(
            model_name='otp',
            name='logged',
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
