from django.db import models
from product.models import Product 
from userProfile.models import Address
from bases.models import BaseModel

# Create your models here.


class ProducerProduct(BaseModel):
    product = models.ForeignKey(Product, models.SET_NULL,blank=True,null=True)
    product_time = models.DateTimeField(auto_now=True)
    amount_of_product = models.CharField(max_length=100, blank=True, null=True)


class ProducerFarm(BaseModel):
    land_amount = models.CharField(max_length=30, blank=True, null=True)
    type_of_crops_produce = models.CharField(max_length=30, blank=True, null=True)
    product_photo = models.ImageField(blank=True, null=True)
    address = models.ForeignKey(Address, models.SET_NULL,blank=True,null=True)