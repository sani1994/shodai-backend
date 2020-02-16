# Generated by Django 2.2.5 on 2020-02-16 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('producer', '0003_auto_20200204_1500'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='microbulkorder',
            name='shareable_ref_code',
        ),
        migrations.AddField(
            model_name='bulkorderproducts',
            name='shareable_ref_code',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
