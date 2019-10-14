from django.db import models
from bases.models import BaseModel
from product.models import Product


# Create your models here.

class Offer(BaseModel):
    # put reailer as foreign key
    offer_name = models.CharField(max_length=100,blank=False,null=False)
    offer_img = models.ImageField(upload_to='static/pictures/offer/%Y/%m/%d',blank=False,null=False)
    offer_details = models.CharField(max_length=500,blank=True,null=True)
    offer_ends_in = models.DateTimeField(blank=True,null=True)
    offer_starts_in = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return self.offer_name


class OfferProduct(BaseModel):
    offer = models.ForeignKey(Offer,on_delete=models.CASCADE) # offr foreign key relation
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    offer_product_balance = models.DecimalField(max_digits=5,decimal_places=1,blank=True,null=True)

    def __str__(self):
        return self.product