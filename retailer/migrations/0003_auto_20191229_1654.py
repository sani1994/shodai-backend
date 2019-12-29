# Generated by Django 2.2.5 on 2019-12-29 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utility', '0001_initial'),
        ('retailer', '0002_auto_20191204_0621'),
    ]

    operations = [
        migrations.AddField(
            model_name='acceptedorder',
            name='shop',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='retailer.Shop'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalacceptedorder',
            name='shop',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='retailer.Shop'),
        ),
        migrations.AddField(
            model_name='historicalshopproduct',
            name='product_unit',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utility.ProductUnit'),
        ),
        migrations.AddField(
            model_name='historicalshopproduct',
            name='shop',
            field=models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='retailer.Shop'),
        ),
        migrations.AddField(
            model_name='shopproduct',
            name='product_unit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='utility.ProductUnit'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shopproduct',
            name='shop',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='retailer.Shop'),
        ),
        migrations.AlterField(
            model_name='acceptedorder',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
