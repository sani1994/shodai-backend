from django.db import models
from bases.models import BaseModel

# Create your models here.

class ShopCategory(BaseModel):
    type_of_shop = models.CharField(max_length=89)

    def __str__(self):
        return self.type_of_shop

class ProductCategory(BaseModel):
    type_of_product = models.CharField(max_length=90)

    def __str__(self):
        return self.type_of_product

class ProductMeta(BaseModel): # Prodect Meta (original product name with comapny name)
    name = models.CharField(max_length=100)
    product_category = models.ForeignKey(ProductCategory, models.SET_NULL,blank=True,null=True)
    shop_category = models.ForeignKey(ShopCategory, models.SET_NULL,blank=True,null=True)

    def __str__(self):
        return self.name

class Product(BaseModel):
    product_name = models.CharField(max_length=100, blank=True, null=True)
    product_unit = models.CharField(max_length=3, blank=True, null=True)
    product_price = models.IntegerField(blank=True, null=True)
    product_meta = models.ForeignKey(ProductMeta, models.SET_NULL,blank=True,null=True)

    def __str__(self):
        return self.product_name




