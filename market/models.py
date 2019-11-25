from django.db import models

# Create your models here.
from bases.models import BaseModel
from product.models import Product
# from utility.models import ProductUnit
from utility.models import ProductUnit, Location, Area


class WholeSellRate(models.Model):
    product= models.ForeignKey(Product,on_delete=models.CASCADE)
    producer_price = models.DecimalField(decimal_places=2,blank=True,null=True,max_digits=8)
    unit = models.ForeignKey(ProductUnit,on_delete=models.CASCADE,null=True,blank=True)
    qty = models.FloatField()
    location = models.ForeignKey(Location,on_delete=models.CASCADE,null=True,blank=True)


class KitchenMarket(BaseModel):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    location = models.ForeignKey(Location,on_delete=models.CASCADE,null=True,blank=True)
    polygon = models.ForeignKey(Area,on_delete=models.CASCADE)
    whole_sell_unit = models.ForeignKey(ProductUnit, related_name='whole_sell_unit', on_delete=models.CASCADE,null=True, blank=True)
    unit = models.ForeignKey(ProductUnit,related_name='kitchen_market_unit',on_delete=models.CASCADE,null=True,blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    whole_sell_price = models.DecimalField(max_digits=8,decimal_places=2)
    whole_sell_qty = models.FloatField()
    qty = models.FloatField()




