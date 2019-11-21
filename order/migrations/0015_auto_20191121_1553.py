# Generated by Django 2.2.5 on 2019-11-21 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0017_auto_20191119_0510'),
        ('order', '0014_historicalorder_historicalorderproduct_historicalvat'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorder',
            name='address',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='userProfile.Address'),
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='userProfile.Address'),
        ),
    ]
