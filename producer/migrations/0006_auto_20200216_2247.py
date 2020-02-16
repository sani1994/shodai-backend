# Generated by Django 2.2.5 on 2020-02-16 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('producer', '0005_bulkorderproducts_available_qty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='microbulkorderproducts',
            name='qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
