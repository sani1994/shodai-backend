# Generated by Django 2.2.5 on 2019-11-25 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utility', '0004_remove_commissionrate_product'),
        ('product', '0016_auto_20191122_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproduct',
            name='product_unit',
            field=models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utility.ProductUnit'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_unit',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='utility.ProductUnit'),
        ),
    ]
