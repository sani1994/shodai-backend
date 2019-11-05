from django.db import models

from product.models import ShopCategory, Product
from userProfile.models import UserProfile
from userProfile.models import Address
from order.models import Order,OrderProduct
from bases.models import BaseModel
# Create your models here.


class Account(BaseModel):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True,blank=True)
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    account_no = models.CharField(max_length=100,blank=True, null=True)
    account_name = models.CharField(max_length=50, blank=True, null=True)


class Shop(BaseModel):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True,blank=True)
    product = models.ManyToManyField(Product)
    shop_name = models.CharField(max_length= 100,null=False,blank=False)
    shop_type = models.ForeignKey(ShopCategory,on_delete=models.CASCADE)
    shop_lat = models.FloatField(null=True,blank=True)
    shop_long = models.FloatField(null=True,blank=True)
    shop_address = models.CharField(max_length=100,blank=True,null=True)
    shop_image= models.ImageField(upload_to='retailer/shop/%Y/%m/%d',null=True,blank=True)
    shop_licence= models.CharField(max_length=200,blank=True,null=True,unique=True) #trade licence
    shop_website = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.shop_name


class AcceptedOrder(BaseModel):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,blank=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    order_product = models.ForeignKey(OrderProduct,on_delete=models.CASCADE,null=True)

    # def __str__(self):
    #     return self.order.






