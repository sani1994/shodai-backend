# Generated by Django 2.2.5 on 2020-01-21 10:00

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BulkOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateTimeField()),
                ('expire_date', models.DateTimeField()),
                ('hex_code', models.CharField(blank=True, default=None, max_length=20, null=True, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BulkOrderProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('general_price', models.FloatField(blank=True, null=True)),
                ('offer_price', models.FloatField(blank=True, null=True)),
                ('target_qty', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('max_qty', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
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
        migrations.CreateModel(
            name='BusinessType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('business_type', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalBusinessType',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('business_type', models.CharField(max_length=100)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical business type',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProducerBulkRequest',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('product_name', models.CharField(max_length=200)),
                ('product_name_bn', models.CharField(blank=True, max_length=100, null=True, verbose_name='পন্যের নাম')),
                ('product_image', models.TextField(blank=True, max_length=100, null=True)),
                ('production_time', models.DateTimeField(blank=True, null=True)),
                ('unit_price', models.FloatField()),
                ('quantity', models.FloatField(blank=True, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('general_price', models.FloatField(blank=True, null=True)),
                ('general_qty', models.FloatField(blank=True, null=True)),
                ('offer_price', models.FloatField(blank=True, null=True)),
                ('offer_qty', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted')], default='Pending', max_length=20)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical producer product',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProducerBusiness',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('business_image', models.TextField(blank=True, max_length=100, null=True)),
                ('total_employees', models.IntegerField(blank=True, null=True)),
                ('land_amount', models.CharField(blank=True, max_length=30, null=True)),
                ('lat', models.FloatField(blank=True, null=True)),
                ('long', models.FloatField(blank=True, null=True)),
                ('product_business_geopoint', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('address', models.CharField(blank=True, max_length=300, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical producer business',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProducerFarm',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('land_amount', models.CharField(blank=True, max_length=30, null=True)),
                ('type_of_crops_produce', models.CharField(blank=True, max_length=30, null=True)),
                ('product_photo', models.TextField(blank=True, max_length=100, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical producer farm',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='MicroBulkOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('shareable_ref_code', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('accepted_ref_code', models.CharField(blank=True, max_length=30, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MicroBulkOrderProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('qty', models.FloatField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProducerBulkRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('product_name', models.CharField(max_length=200)),
                ('product_name_bn', models.CharField(blank=True, max_length=100, null=True, verbose_name='পন্যের নাম')),
                ('product_image', models.ImageField(blank=True, null=True, upload_to='producer/product')),
                ('production_time', models.DateTimeField(blank=True, null=True)),
                ('unit_price', models.FloatField()),
                ('quantity', models.FloatField(blank=True, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('general_price', models.FloatField(blank=True, null=True)),
                ('general_qty', models.FloatField(blank=True, null=True)),
                ('offer_price', models.FloatField(blank=True, null=True)),
                ('offer_qty', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted')], default='Pending', max_length=20)),
            ],
            options={
                'verbose_name': 'producer product',
                'verbose_name_plural': 'Producer Bulk Request',
            },
        ),
        migrations.CreateModel(
            name='ProducerBusiness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('business_image', models.ImageField(blank=True, null=True, upload_to='producer/business')),
                ('total_employees', models.IntegerField(blank=True, null=True)),
                ('land_amount', models.CharField(blank=True, max_length=30, null=True)),
                ('lat', models.FloatField(blank=True, null=True)),
                ('long', models.FloatField(blank=True, null=True)),
                ('product_business_geopoint', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('address', models.CharField(blank=True, max_length=300, null=True)),
                ('is_approved', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProducerFarm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('land_amount', models.CharField(blank=True, max_length=30, null=True)),
                ('type_of_crops_produce', models.CharField(blank=True, max_length=30, null=True)),
                ('product_photo', models.ImageField(blank=True, null=True, upload_to='')),
                ('is_approved', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
