
from django.db import models
from userProfile.models import UserProfile
from product.models import ProductMeta
from product.models import Product
from bases.models import BaseModel

# Create your models here.



class Order(BaseModel):
    user = models.ForeignKey(UserProfile, models.SET_NULL,blank=True,null=True)
    delivery_date_time = models.DateTimeField(auto_now=True)
    delivery_place = models.CharField(max_length=100)
    
    ORDERED = 'OD'              # ORDER COLLECT FROM CUSTOMER
    ORDER_READY = 'RE'          # ORDER IS READY FOR DELIVERY PERSON
    ORDER_AT_DELIVERY = 'OAD'   # ORDER IS WITH DELIVERY PEROSN
    ORDER_COMPLETED = 'COM'      # ORDER IS DELIVERED TO CUSTOMER
    ORDER_CANCELLED = 'CN'      # ORDER IS CANCEL BY CUSTOMER
    ORDER_STATUS = [
        (ORDERED, 'Ordered'),
        (ORDER_READY, 'Order Ready'),
        (ORDER_AT_DELIVERY, 'Order At Delivery'),
        (ORDER_COMPLETED, 'Order Completed'),
        (ORDER_CANCELLED, 'Order Cancelled'),
    ]
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default=ORDERED)
    home_delivery = models.BooleanField(default=True)

    FIXED_PRICE = 'FP'
    BIDDING = 'BD'
    ORDER_TYPES = [
        (FIXED_PRICE, 'Fixed Price'),
        (BIDDING, 'Biding'),
    ]
    order_type = models.CharField(max_length=20,choices=ORDER_TYPES,default=FIXED_PRICE)
    contact_number = models.IntegerField(max_length=15,null=True,blank=True)

    def __str__(self):
        return self.delivery_place



class OrderProduct(BaseModel):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    orderproduct_qty = models.FloatField(default=1)

class Vat(BaseModel):
    product_meta = models.ForeignKey(ProductMeta, models.SET_NULL,blank=True,null=True)
    vat_amount = models.FloatField(blank=True,null=True)
    





