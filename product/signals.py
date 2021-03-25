from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django_q.tasks import async_task

from product.models import Product


@receiver(pre_save, sender=Product)
def product_data_preprocessing(sender, instance, **kwargs):
    if instance.id:
        previous_instance = Product.objects.get(id=instance.id)
        if instance.product_price != previous_instance.product_price:
            instance.product_last_price = previous_instance.product_price
    else:
        instance.product_last_price = instance.product_price

    if instance.product_meta.vat_amount:
        instance.price_with_vat = round(float(instance.product_price) + (float(instance.product_price) * instance.product_meta.vat_amount) / 100)
    else:
        instance.price_with_vat = instance.product_price

    instance.slug = slugify(instance.product_name) + "-" + slugify(instance.product_unit.product_unit)
    # instance.product_sku = "{}-{}-{}-{}".format(instance.product_meta.product_category.code,
    #                                             instance.product_meta.code,
    #                                             instance.product_manufacturer.code,
    #                                             instance.code)


# @receiver(post_save, sender=Product)
# def product_created_or_updated(sender, instance, created, **kwargs):
#     async_task('product.tasks.send_product_data', instance)
