# Generated by Django 2.2.5 on 2020-01-21 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_auto_20200120_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproduct',
            name='product_description_bn',
            field=models.CharField(default=' ', max_length=200),
        ),
        migrations.AddField(
            model_name='product',
            name='product_description_bn',
            field=models.CharField(default=' ', max_length=200),
        ),
    ]
