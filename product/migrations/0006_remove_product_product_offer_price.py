# Generated by Django 2.2.5 on 2019-10-14 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_auto_20191014_0753'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_offer_price',
        ),
    ]