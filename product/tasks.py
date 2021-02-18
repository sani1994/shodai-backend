import json
import requests
from django.conf import settings


def send_product_info(data):
    data = json.loads(data)
    product_id = data[0]['pk']
    product_data = data[0]['fields']

    payload = {"product_id": product_id,
               "product_meta_id": product_data['product_meta'],
               "product_unit_id": product_data['product_unit'],
               "product_name": product_data['product_name'],
               "product_name_bn": product_data['product_name_bn'],
               "product_image_url": settings.API_DOMAIN + '/media/' + product_data['product_image'],
               "product_description": product_data['product_description'],
               "product_description_bn": product_data['product_description_bn'],
               "product_price": product_data['product_price'],
               "product_price_bn": product_data['product_price_bn'],
               "product_last_price": product_data['product_last_price'],
               "price_with_vat": product_data['price_with_vat'],
               "slug": product_data['slug'],
               "is_approved": product_data['is_approved']}

    url = settings.INTERNAL_BRICKBOX_API_URL + '/shodai/product'
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, headers=headers, json=payload).json()
    return response
