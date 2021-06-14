from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from user.models import UserProfile


@receiver(post_save, sender=UserProfile)
def user_profile_created_or_updated(sender, instance, created, **kwargs):
    async_task('user.tasks.send_customer_data', instance)
