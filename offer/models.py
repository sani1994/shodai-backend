from django.db import models
from simple_history.models import HistoricalRecords

from bases.models import BaseModel
from product.models import Product


# Create your models here.

class Offer(BaseModel):
    # put reailer as foreign key
    offer_name = models.CharField(max_length=100, blank=False, null=False)
    offer_name_bn = models.CharField(max_length=100, blank=False, null=False)
    offer_img = models.ImageField(upload_to="offer", blank=False, null=False)
    offer_details = models.CharField(max_length=500, blank=True, null=True)
    offer_details_bn = models.CharField(max_length=500, blank=True, null=True, verbose_name='Offer Detail Bangla')
    offer_starts_in = models.DateTimeField(blank=True, null=True)
    offer_ends_in = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

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
