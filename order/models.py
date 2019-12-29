from django.db import models
from simple_history.models import HistoricalRecords

from userProfile.models import UserProfile
from product.models import ProductMeta
from product.models import Product
from bases.models import BaseModel
from userProfile.models import Address

# Create your models here.


class Order(BaseModel):
    user = models.ForeignKey(UserProfile, models.SET_NULL,blank=True,null=True)
    delivery_date_time = models.DateTimeField(auto_now=True)
    delivery_place = models.CharField(max_length=100)
    order_total_price = models.FloatField(default=0)
    lat = models.FloatField()
    long=models.FloatField()
    
    ORDERED = 'OD'              # ORDER COLLECT FROM CUSTOMER
    ORDER_ACCEPTED = 'OA'        #ORDER ACCEPTED BY RETAILER OR PRODUCER
    ORDER_READY = 'RE'          # ORDER IS READY FOR DELIVERY PERSON
    ORDER_AT_DELIVERY = 'OAD'   # ORDER IS WITH DELIVERY PEROSN
    ORDER_COMPLETED = 'COM'      # ORDER IS DELIVERED TO CUSTOMER
    ORDER_CANCELLED = 'CN'      # ORDER IS CANCEL BY CUSTOMER
    ORDER_STATUS = [
        (ORDERED, 'Ordered'),
        (ORDER_ACCEPTED, 'Order Accepted'),
        (ORDER_READY, 'Order Ready'),
        (ORDER_AT_DELIVERY, 'Order At Delivery'),
        (ORDER_COMPLETED, 'Order Completed'),
        (ORDER_CANCELLED, 'Order Cancelled'),
    ]
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default=ORDERED)
    home_delivery = models.BooleanField(default=True,null=False,blank=False)
    address = models.ForeignKey(Address,on_delete=models.CASCADE,null=True)

    FIXED_PRICE = 'FP'
    BIDDING = 'BD'
    ORDER_TYPES = [
        (FIXED_PRICE, 'Fixed Price'),
        (BIDDING, 'Biding'),
    ]
    order_type = models.CharField(max_length=20,choices=ORDER_TYPES,default=FIXED_PRICE)
    contact_number = models.CharField(max_length=20,null=True,blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.user.username


class OrderProduct(BaseModel):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    order_product_price = models.FloatField(blank=False,null=False,default=0)  # product may belong to offer do the price
    order_product_qty = models.FloatField(default=1)
    history = HistoricalRecords()

    def __str__(self):
        return self.product.product_name


class Vat(BaseModel):
    product_meta = models.ForeignKey(ProductMeta, on_delete=models.CASCADE,blank=False,null=False,default=None)
    vat_amount = models.FloatField(default=0,blank=False,null=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.product_meta.name
    




