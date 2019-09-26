
from django.db import models
from userProfile.models import UserProfile
from product.models import ProductMeta
from product.models import Product
from bases.models import BaseModel

# Create your models here.



class Order(BaseModel):
    user_id = models.ForeignKey(UserProfile, models.SET_NULL,blank=True,null=True)
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



class OrderProduct(BaseModel):
    product_id = models.ForeignKey(Product, models.SET_NULL,
    blank=True,
    null=True)
    order_id = models.ForeignKey(Order, models.SET_NULL,
    blank=True,
    null=True)

class Vat(BaseModel):
    product_meta = models.ForeignKey(ProductMeta, models.SET_NULL,
    blank=True,
    null=True)
    vat_amount = models.IntegerField(default=True)
    





