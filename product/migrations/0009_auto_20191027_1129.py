# Generated by Django 2.2.5 on 2019-10-27 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_auto_20191015_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_image',
            field=models.ImageField(default=1, upload_to='pictures/product/'),
            preserve_default=False,
        ),
    ]