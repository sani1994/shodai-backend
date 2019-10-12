from django.db import models
from bases.models import BaseModel
from product.models import Product


# Create your models here.

class OfferImage(BaseModel):
    offer_name = models.CharField(max_length=100,blank=False,null=False)
    offer_img = models.ImageField(upload_to='pictures/offer/%Y/%m/%d',blank=False,null=False)
    offer_details = models.CharField(blank=True,null=True)

    def __str__(self):
        return self.offer_name


class OfferProduct(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product