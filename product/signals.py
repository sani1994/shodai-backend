from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from product.models import Product


@receiver(post_save, sender=Product)
def product_created_or_updated(sender, instance, created, **kwargs):
    async_task('product.tasks.send_product_data', instance, created)
