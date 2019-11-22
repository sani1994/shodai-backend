from django.db import models

# Create your models here.
from bases.models import BaseModel
from product.models import Product
# from utility.models import ProductUnit
from utility.models import ProductUnit, Location, Area


class WholeSellRate(models.Model): #write serializer
    product= models.ForeignKey(Product,on_delete=models.CASCADE)
    producer_price = models.DecimalField(decimal_places=2,blank=True,null=True,max_digits=8)
    unit = models.ForeignKey(ProductUnit,on_delete=models.CASCADE,null=True,blank=True)
    qty = models.FloatField()
    location = models.ForeignKey(Location,on_delete=models.CASCADE,null=True,blank=True)


class KitchenMarket(BaseModel): #write serializer
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    qty = models.FloatField()
    unit = models.ForeignKey(ProductUnit,related_name='kitchen_market_unit',on_delete=models.CASCADE,null=True,blank=True)
    whole_sell_price = models.DecimalField(max_digits=8,decimal_places=2)
    whole_sell_qty = models.FloatField()
    whole_sell_unit = models.ForeignKey(ProductUnit,related_name='whole_sell_unit',on_delete=models.CASCADE,null=True,blank=True)
    location = models.ForeignKey(Location,on_delete=models.CASCADE,null=True,blank=True)
    polygon = models.ForeignKey(Area,on_delete=models.CASCADE)



