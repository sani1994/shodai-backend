from django.db import models
from simple_history.models import HistoricalRecords

from bases.models import BaseModel
from product.models import Product


# Create your models here.

class Offer(BaseModel):
    # put retailer as foreign key
    offer_name = models.CharField(max_length=100, blank=False, null=False)
    offer_name_bn = models.CharField(max_length=100, blank=False, null=False)
    offer_img = models.ImageField(upload_to="offer", blank=False, null=False)
    offer_details = models.CharField(max_length=500, blank=True, null=True)
    offer_details_bn = models.CharField(max_length=500, blank=True, null=True, verbose_name='Offer Detail Bangla')
    offer_starts_in = models.DateTimeField(blank=True, null=True)
    offer_ends_in = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    SINGLE_PRODUCT_OFFER = 'SP'  # Offer on a single product
    BUNDLE_OFFER = 'BP'  # Offer on a bundle product
    DISCOUNT_ON_SINGLE_PRODUCT = 'DSP'  # Discount on a single product based on total amount
    DISCOUNT_ON_TOTAL = 'DT'  # Discount on total based on total amount
    DISCOUNT_ON_DELIVERY_CHARGE = 'DD'  # Discount on delivery charge based on total amount
    OFFER_TYPES = [
        (SINGLE_PRODUCT_OFFER, 'Single Product Offer'),
        (BUNDLE_OFFER, 'Bundle Offer'),
        (DISCOUNT_ON_SINGLE_PRODUCT, 'Discount on Single Product'),
        (DISCOUNT_ON_TOTAL, 'Discount on Total'),
        (DISCOUNT_ON_DELIVERY_CHARGE, 'Discount on Delivery Charge'),
    ]
    order_types = models.CharField(max_length=100, choices=OFFER_TYPES, default=SINGLE_PRODUCT_OFFER)

    def __str__(self):
        return self.offer_name


class OfferProduct(BaseModel):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)  # offer foreign key relation
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    offer_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    offer_product_balance = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.product.product_name

    def get_offer_product_url(self):
        return "https://www.shod.ai/admin/offer/offerproduct/%d/change/" % self.id


class CartOffer(BaseModel):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    sub_total_limit = models.IntegerField(default=0)
    updated_shipping_charge = models.FloatField(default=0)
    discount_amount = models.FloatField(default=0, blank=False, null=False, verbose_name='Discount Amount(%)')
    discount_limit = models.IntegerField(default=0)
    history = HistoricalRecords()

    def __str__(self):
        return self.offer.offer_name + " on " + self.sub_total_limit


class CouponCode(BaseModel):
    cart_offer = models.ForeignKey(CartOffer, on_delete=models.CASCADE)
