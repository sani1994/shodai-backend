import requests
from django.conf import settings


headers = {"Content-Type": "application/json",
           "Accept": "application/json",
           "Authorization": "Bearer {}".format(settings.INTERNAL_BRICKBOX_API_KEY)}


def send_product_category_data(product_category, created):
    payload = {"product_category_id": product_category.id,
               "product_category_code": None,
               "product_category_name": product_category.type_of_product,
               "product_category_name_bn": product_category.type_of_product_bn,
               "product_category_image_url": settings.WEB_DOMAIN + product_category.img.url if product_category.img else None,
               "parent_product_category_id": product_category.parent.id if product_category.parent else None}

    if not settings.DEBUG:
        if created:
            url = settings.INTERNAL_BRICKBOX_API_URL + '/product/category'
            response = requests.post(url, headers=headers, json=payload).json()
        else:
            url = settings.INTERNAL_BRICKBOX_API_URL + f'/product/category/{product_category.id}'
            response = requests.put(url, headers=headers, json=payload).json()
        return response
    else:
        return 'in debug mode'


def send_product_data(product, created):
    payload = {"product_id": product.id,
               "product_code": None,
               "product_sku": None,
               "product_name": product.product_name,
               "product_name_bn": product.product_name_bn,
               "product_description": product.product_description,
               "product_description_bn": product.product_description_bn,
               "product_image_url": settings.WEB_DOMAIN + product.product_image.url if product.product_image else None,
               "product_price": float(product.product_price),
               "product_last_price": float(product.product_last_price),
               "product_vat_percentage": product.product_meta.vat_amount,
               "product_unit": product.product_unit.product_unit,
               "product_unit_bn": product.product_unit.product_unit_bn,
               "slug": product.slug,
               "is_approved": product.is_approved,
               "product_category_id": product.product_category.id,
               # "product_manufacturer_id": None,
               # "product_manufacturer_code": None,
               # "product_manufacturer_name": "",
               # "product_manufacturer_name_bn": "",
               # "product_manufacturer_address": "",
               # "product_manufacturer_contact_number": "",
               # "product_manufacturer_email": ""
               }

    if not settings.DEBUG:
        if created:
            url = settings.INTERNAL_BRICKBOX_API_URL + '/product'
            response = requests.post(url, headers=headers, json=payload).json()
        else:
            url = settings.INTERNAL_BRICKBOX_API_URL + f'/product/{product.id}'
            response = requests.put(url, headers=headers, json=payload).json()
        return response
    else:
        return 'in debug mode'
