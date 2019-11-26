# Generated by Django 2.2.5 on 2019-11-26 07:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0001_initial'),
        ('offer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerproduct',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='User who created it', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_offer_offerproduct_set', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AddField(
            model_name='offerproduct',
            name='modified_by',
            field=models.ForeignKey(blank=True, help_text='User who last modified', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified_offer_offerproduct_set', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='offerproduct',
            name='offer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offer.Offer'),
        ),
        migrations.AddField(
            model_name='offerproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product'),
        ),
        migrations.AddField(
            model_name='offer',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='User who created it', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_offer_offer_set', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AddField(
            model_name='offer',
            name='modified_by',
            field=models.ForeignKey(blank=True, help_text='User who last modified', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified_offer_offer_set', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='historicalofferproduct',
            name='created_by',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='User who created it', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AddField(
            model_name='historicalofferproduct',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalofferproduct',
            name='modified_by',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='User who last modified', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='historicalofferproduct',
            name='offer',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='offer.Offer'),
        ),
        migrations.AddField(
            model_name='historicalofferproduct',
            name='product',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='product.Product'),
        ),
        migrations.AddField(
            model_name='historicaloffer',
            name='created_by',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='User who created it', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AddField(
            model_name='historicaloffer',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicaloffer',
            name='modified_by',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='User who last modified', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
    ]
