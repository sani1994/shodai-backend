# Generated by Django 2.2.5 on 2019-12-03 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('producer', '0018_auto_20191201_0650'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkorderproducts',
            name='max_qty',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='microbulkorder',
            name='accepted_ref_code',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='microbulkorder',
            name='shareable_ref_code',
            field=models.CharField(default=None, max_length=100, unique=True),
        ),
        migrations.DeleteModel(
            name='CustomerMicroBulkOrderProductRequest',
        ),
    ]
