# Generated by Django 2.2.5 on 2019-11-24 04:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ShopInventoryHistory',
        ),
    ]
