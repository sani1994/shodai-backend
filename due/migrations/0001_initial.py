# Generated by Django 2.2.5 on 2019-12-04 06:21

from django.db import migrations, models
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalUserDues',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('debit', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('credit', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical user dues',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='UserDues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('debit', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('credit', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserDuesHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debit', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('credit', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
            ],
        ),
    ]
