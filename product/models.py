from django.db import models
from bases.models import BaseModel

# Create your models here.


class ShopCategory(BaseModel):
    type_of_shop = models.CharField(max_length=89)

    def __str__(self):
        return self.type_of_shop


class ProductCategory(BaseModel):
    type_of_product = models.CharField(max_length=90)
    img = models.ImageField(upload_to='static/pictures/productcategory/', blank=True, null=True)

    def __str__(self):
        return self.type_of_product


class ProductMeta(BaseModel): # Prodect Meta (original product name with comapny name)
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to="static/pictures/productmeta/", blank=True, null=True)
    product_category = models.ForeignKey(ProductCategory,on_delete=models.CASCADE)
    shop_category = models.ForeignKey(ShopCategory,on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(BaseModel):
    # put retailer as foreign key
    product_name = models.CharField(max_length=100, blank=True, null=True)
    product_image = models.ImageField(upload_to='static/pictures/product/%Y/%m/%d/', blank=True, null=True)
    product_unit = models.CharField(max_length=3, blank=True, null=True)
    product_price = models.DecimalField(decimal_places=2,max_digits=7,blank=True, null=True)
    # product_offer_price = models.DecimalField(decimal_places=2,max_digits=7,blank=True,null=True)
    product_meta = models.ForeignKey(ProductMeta, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name




