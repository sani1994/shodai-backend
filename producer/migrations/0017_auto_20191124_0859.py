# Generated by Django 2.2.5 on 2019-11-24 08:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utility', '0003_remarks'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('producer', '0016_auto_20191124_0457'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulkOrderReqConnector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='bulkorder',
            name='hex_code',
            field=models.CharField(default='none', max_length=20),
        ),
        migrations.AddField(
            model_name='bulkorderproducts',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utility.ProductUnit'),
        ),
        migrations.AddField(
            model_name='historicalproducerbulkrequest',
            name='general_unit',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utility.ProductUnit'),
        ),
        migrations.AddField(
            model_name='historicalproducerbulkrequest',
            name='offer_unit',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utility.ProductUnit'),
        ),
        migrations.AddField(
            model_name='historicalproducerbulkrequest',
            name='unit',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utility.ProductUnit'),
        ),
        migrations.AddField(
            model_name='producerbulkrequest',
            name='general_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='general_unit', to='utility.ProductUnit'),
        ),
        migrations.AddField(
            model_name='producerbulkrequest',
            name='offer_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offer_unit', to='utility.ProductUnit'),
        ),
        migrations.AddField(
            model_name='producerbulkrequest',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='producer_unit', to='utility.ProductUnit'),
        ),
        migrations.DeleteModel(
            name='BulkOrderReqConntr',
        ),
        migrations.AddField(
            model_name='bulkorderreqconnector',
            name='bulk_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='producer.BulkOrder'),
        ),
        migrations.AddField(
            model_name='bulkorderreqconnector',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='User who created it', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_producer_bulkorderreqconnector_set', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AddField(
            model_name='bulkorderreqconnector',
            name='modified_by',
            field=models.ForeignKey(blank=True, help_text='User who last modified', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified_producer_bulkorderreqconnector_set', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='bulkorderreqconnector',
            name='producer_bulk_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='producer.ProducerBulkRequest'),
        ),
    ]
