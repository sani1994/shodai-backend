import requests
from decouple import config

import logging

otp_text = "{} - OTP for Shodai Login. Valid for next five (5) minutes."


def send_sms_otp(mobile_number, sms_content):
    url = "https://portal.adnsms.com/api/v1/secure/send-sms"
    body = {
        "api_key": "KEY-ft8r3q3h5jih9ubrcjhl9t7cgyl1uxlk",
        "api_secret": "zPEO4n!OY1KOdqMq",
        "request_type": "OTP",
        "message_type": "Text",
        "mobile": mobile_number,
        "message_body": sms_content
    }
    response = requests.post(url, data=body).json()
    logging.info("otp sending response: {}".format(response))
    if response["api_response_message"] == "SUCCESS":
        return True
    else:
        logging.critical("otp error for {}".format(mobile_number))
        return False
