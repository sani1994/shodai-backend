from django.db import models
from simple_history.models import HistoricalRecords

from product.models import ProductCategory
from userProfile.models import Address, UserProfile
from bases.models import BaseModel
from django.contrib.gis.db import models
# Create your models here.


class ProducerProduct(BaseModel):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200,null=False,blank=False)
    product_image = models.ImageField(upload_to='producer/product',null=True,blank=True)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    production_time = models.DateTimeField(null=True,blank=True)
    unit_price = models.FloatField(null=False,blank=False)
    delivery_amount = models.FloatField(blank=True,null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name


class BusinessType(BaseModel):
    business_type = models.CharField(max_length=100)
    history = HistoricalRecords()

    def __str__(self):
        return self.business_type


class ProducerBusiness(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    business_image = models.ImageField(upload_to='producer/business',blank=True,null=True)
    business_type = models.ForeignKey(BusinessType,on_delete=models.CASCADE)
    total_employees = models.IntegerField(null=True,blank=True)
    land_amount = models.CharField(max_length=30, blank=True, null=True)
    lat = models.FloatField(blank=True,null=True)
    long = models.FloatField(blank=True,null=True)
    productbusiness_geopoint = models.PointField(null=True)
    address = models.CharField(max_length=300,blank=True,null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.shop_lat = self.productbusiness_geopoint.y
        self.shop_long = self.productbusiness_geopoint.x
        super(ProducerBusiness, self).save(*args, **kwargs)


class ProducerFarm(BaseModel):
    land_amount = models.CharField(max_length=30, blank=True, null=True)
    type_of_crops_produce = models.CharField(max_length=30, blank=True, null=True)
    product_photo = models.ImageField(blank=True, null=True)
    address = models.ForeignKey(Address, models.SET_NULL,blank=True,null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.type_of_crops_produce