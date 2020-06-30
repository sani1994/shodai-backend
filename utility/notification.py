from decouple import config
from django.core.mail import send_mail
from requests import post
from sodai import settings


def email_notification(subject, body):
    # target_user = ['rana@shod.ai', 'shishir@shod.ai', 'support@shod.ai', 'mohua@finder-lbs.com']
    target_user = config("TARGET_EMAIL_USER").replace(" ", "").split(',')
    return send_mail(subject, body, settings.EMAIL_HOST_USER, target_user)


def send_sms(mobile_number, sms_content):
    url = "https://portal.adnsms.com/api/v1/secure/send-sms"
    body = {
        "api_key": config("OTP_SECRET", None),
        "api_secret": config("OTP_API_KEY", None),
        "request_type": "single_sms",
        "message_type": "Text",
        "mobile": mobile_number,
        "message_body": sms_content
    }

    response = post(url, data=body).json()

    if response["api_response_message"] == "SUCCESS":
        return 'success'
    else:
        return 'failed'
