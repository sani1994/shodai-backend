import requests
from django.conf import settings


headers = {"Content-Type": "application/json",
           "Accept": "application/json",
           "Authorization": "Bearer {}".format(settings.INTERNAL_BRICKBOX_API_KEY)}


def send_customer_data(customer, created):
    payload = {"customer_id": customer.id,
               "customer_name": customer.first_name,
               "customer_mobile_number": customer.mobile_number,
               "customer_email": customer.email if customer.email else ""}

    if not settings.DEBUG:
        if created:
            url = settings.INTERNAL_BRICKBOX_API_URL + '/customer'
            response = requests.post(url, headers=headers, json=payload).json()
        else:
            url = settings.INTERNAL_BRICKBOX_API_URL + f'/customer/{customer.id}'
            response = requests.put(url, headers=headers, json=payload).json()
        return response
    else:
        return 'in debug mode'
