from django.db import models
from product.models import ProductCategory
from userProfile.models import Address
from bases.models import BaseModel

# Create your models here.


class ProducerProduct(BaseModel):
    product_name = models.CharField(max_length=200)
    product_image = models.ImageField(upload_to='producer/product')
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    production_time = models.DateTimeField()
    unit_price = models.FloatField()
    delivery_amount = models.FloatField(blank=True,null=True)

    def __str__(self):
        return self.product_name


class BusinessType(BaseModel):
    business_type = models.CharField(max_length=100)

    def __str__(self):
        return self.business_type

class ProducerBusiness(BaseModel):
    business_type = models.ForeignKey(BusinessType,on_delete=models.CASCADE)
    total_employees = models.IntegerField()
    land_amount = models.CharField(max_length=30, blank=True, null=True)
    lat = models.FloatField(blank=True,null=True)
    long = models.FloatField(blank=True,null=True)
    address = models.CharField(blank=True,null=True)


class ProducerFarm(BaseModel):
    land_amount = models.CharField(max_length=30, blank=True, null=True)
    type_of_crops_produce = models.CharField(max_length=30, blank=True, null=True)
    product_photo = models.ImageField(blank=True, null=True)
    address = models.ForeignKey(Address, models.SET_NULL,blank=True,null=True)