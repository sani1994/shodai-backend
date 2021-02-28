import requests
from django.conf import settings


headers = {"Content-Type": "application/json",
           "Accept": "application/json",
           "Authorization": "Bearer {}".format(settings.INTERNAL_BRICKBOX_API_TOKEN)}


def send_product_data(product, created):
    payload = {"product_name": product.product_name,
               "product_name_bn": product.product_name_bn,
               "product_description": product.product_description,
               "product_description_bn": product.product_description_bn,
               "product_image_url": settings.API_DOMAIN + product.product_image.url if product.product_image else None,
               "product_price": product.product_price,
               "product_last_price": product.product_last_price,
               "product_vat_percentage": product.product_meta.vat_amount,
               "product_unit": product.product_unit.product_unit,
               "product_unit_bn": product.product_unit.product_unit_bn,
               "slug": product.slug,
               "product_category_id": product.product_meta.product_category.id,
               "product_category_name": product.product_meta.product_category.type_of_product,
               "product_category_name_bn": product.product_meta.product_category.type_of_product_bn,
               "product_category_image_url": settings.API_DOMAIN + product.product_meta.product_category.img.url if product.product_meta.product_category.img else None,
               "product_subcategory_id": product.product_meta.id,
               "product_subcategory_name": product.product_meta.name,
               "product_subcategory_name_bn": product.product_meta.name_bn,
               "product_subcategory_image_url": settings.API_DOMAIN + product.product_meta.img.url if product.product_meta.img else None,
               "is_approved": product.is_approved}

    if created:
        payload["product_id"] = product.id
        url = settings.INTERNAL_BRICKBOX_API_URL + '/shodai/product'
        response = requests.post(url, headers=headers, json=payload).json()
    else:
        url = settings.INTERNAL_BRICKBOX_API_URL + '/shodai/product/{}'.format(product.id)
        response = requests.put(url, headers=headers, json=payload).json()
    return response
