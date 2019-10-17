# Generated by Django 2.2.5 on 2019-10-17 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retailer', '0003_auto_20191016_1352'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='retailer_id',
        ),
        migrations.AddField(
            model_name='shop',
            name='shop_website',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='shop',
            name='shop_licence',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
        migrations.DeleteModel(
            name='Retailer',
        ),
    ]
