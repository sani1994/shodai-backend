# Generated by Django 2.2.5 on 2020-02-04 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retailer', '0008_auto_20200202_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acceptedorder',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalacceptedorder',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalaccount',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalshop',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalshopproduct',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shop',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shopproduct',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
