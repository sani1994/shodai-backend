# Generated by Django 2.2.5 on 2019-11-26 07:45

from django.db import migrations, models
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalOrder',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('delivery_date_time', models.DateTimeField(blank=True, editable=False)),
                ('delivery_place', models.CharField(max_length=100)),
                ('order_total_price', models.FloatField(default=0)),
                ('lat', models.FloatField()),
                ('long', models.FloatField()),
                ('order_status', models.CharField(choices=[('OD', 'Ordered'), ('OA', 'Order Accepted'), ('RE', 'Order Ready'), ('OAD', 'Order At Delivery'), ('COM', 'Order Completed'), ('CN', 'Order Cancelled')], default='OD', max_length=100)),
                ('home_delivery', models.BooleanField(default=True)),
                ('order_type', models.CharField(choices=[('FP', 'Fixed Price'), ('BD', 'Biding')], default='FP', max_length=20)),
                ('contact_number', models.CharField(blank=True, max_length=20, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical order',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrderProduct',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('order_product_price', models.FloatField(default=0)),
                ('order_product_qty', models.FloatField(default=1)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical order product',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalVat',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('vat_amount', models.FloatField(default=0)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical vat',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('delivery_date_time', models.DateTimeField(auto_now=True)),
                ('delivery_place', models.CharField(max_length=100)),
                ('order_total_price', models.FloatField(default=0)),
                ('lat', models.FloatField()),
                ('long', models.FloatField()),
                ('order_status', models.CharField(choices=[('OD', 'Ordered'), ('OA', 'Order Accepted'), ('RE', 'Order Ready'), ('OAD', 'Order At Delivery'), ('COM', 'Order Completed'), ('CN', 'Order Cancelled')], default='OD', max_length=100)),
                ('home_delivery', models.BooleanField(default=True)),
                ('order_type', models.CharField(choices=[('FP', 'Fixed Price'), ('BD', 'Biding')], default='FP', max_length=20)),
                ('contact_number', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('order_product_price', models.FloatField(default=0)),
                ('order_product_qty', models.FloatField(default=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('vat_amount', models.FloatField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
