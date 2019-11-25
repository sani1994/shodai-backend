import random

from django.db import models
from simple_history.models import HistoricalRecords

from order.models import Order
from product.models import ProductCategory, Product
from userProfile.models import Address, UserProfile
from bases.models import BaseModel
from django.contrib.gis.db import models
# Create your models here.
from utility.models import ProductUnit


class ProducerBulkRequest(BaseModel):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True,blank=True)
    product_name = models.CharField(max_length=200,null=False,blank=False)
    product_image = models.ImageField(upload_to='producer/product',null=True,blank=True)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    unit=models.ForeignKey(ProductUnit,on_delete=models.CASCADE,related_name='producer_unit',null=True,blank=True)
    production_time = models.DateTimeField(null=True,blank=True)
    unit_price = models.FloatField(null=False,blank=False)
    quantity = models.FloatField(blank=True,null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)
    general_price = models.FloatField(null=True,blank=True)
    general_qty=models.FloatField(blank=True,null=True)
    general_unit = models.ForeignKey(ProductUnit,on_delete=models.CASCADE,related_name='general_unit',blank=True,null=True)
    offer_price=models.FloatField(null=True,blank=True)
    offer_qty=models.FloatField(blank=True,null=True)
    offer_unit=models.ForeignKey(ProductUnit,on_delete=models.CASCADE,related_name='offer_unit',blank=True,null=True)


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


class BulkOrder(BaseModel):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True,blank=True)
    expire_date=models.DateTimeField(blank=False,null=False)
    start_date=models.DateTimeField(auto_now=True)
    hex_code = models.CharField(max_length=20,default='none')

    # @property
    # def hex_code(self):
    #     random_number = random.randint(0,99999999)
    #     return hex(random_number)


class BulkOrderProducts(BaseModel):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    bulk_order=models.ForeignKey(BulkOrder,on_delete=models.CASCADE)
    general_price=models.FloatField(blank=True,null=True)
    offer_price=models.FloatField(blank=True,null=True)
    target_qty=models.DecimalField(decimal_places=2,blank=True,null=True,max_digits=5)
    unit = models.ForeignKey(ProductUnit,on_delete=models.CASCADE,blank=True,null=True)


class MicroBulkOrder(BaseModel):
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE)
    customer=models.ForeignKey(UserProfile,on_delete=models.CASCADE)


class MicroBulkOrderProducts(BaseModel):
    bulk_order_products=models.ForeignKey(BulkOrderProducts,on_delete=models.CASCADE)
    micro_bulk_order=models.ForeignKey(MicroBulkOrder,on_delete=models.CASCADE)
    qty=models.DecimalField(decimal_places=2,blank=True,null=True,max_digits=5)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


class BulkOrderReqConnector(BaseModel):
    bulk_order = models.ForeignKey(BulkOrder,on_delete=models.CASCADE)
    producer_bulk_request = models.ForeignKey(ProducerBulkRequest,on_delete=models.CASCADE)