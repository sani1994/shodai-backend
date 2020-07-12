from decouple import config
from django.core.mail import send_mail
from requests import post
from sodai import settings

otp_text = "{} - OTP for Shodai Login. Valid for next five (5) minutes."


def email_notification(subject, body):
    target_user = config("TARGET_EMAIL_USER").replace(" ", "").split(',')
    return send_mail(subject, body, settings.EMAIL_HOST_USER, target_user)


def send_sms(mobile_number, sms_content):
    url = config("SMS_API_URL", None)
    body = {
        "api_key": config("SMS_API_KEY", None),
        "api_secret": config("SMS_API_SECRET", None),
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


def send_sms_otp(mobile_number, sms_content):
    url = config("SMS_API_URL", None)
    body = {
        "api_key": config("SMS_API_KEY", None),
        "api_secret": config("SMS_API_SECRET", None),
        "request_type": "OTP",
        "message_type": "Text",
        "mobile": mobile_number,
        "message_body": sms_content
    }

    response = post(url, data=body).json()

    if response["api_response_message"] == "SUCCESS":
        return 'success'
    else:
        return 'failed'
