# Generated by Django 2.2.5 on 2019-10-26 09:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('retailer', '0013_auto_20191026_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acceptedorder',
            name='user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]