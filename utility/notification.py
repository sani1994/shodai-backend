from django.core.mail import send_mail

from sodai import settings


def email_notification(subject,body):
    target_user = ['rana@shod.ai', 'shisir@shod.ai', 'support@shod.ai']
    return send_mail(subject,body,settings.EMAIL_HOST_USER, target_user)


