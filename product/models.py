from django.db import models
from simple_history.models import HistoricalRecords
from bases.models import BaseModel

# Create your models here.
# from utility.models import ProductUnit


class ShopCategory(BaseModel):
    type_of_shop = models.CharField(max_length=89)
    history = HistoricalRecords()

    def __str__(self):
        return self.type_of_shop


class ProductCategory(BaseModel):
    type_of_product = models.CharField(max_length=90)
    img = models.ImageField(upload_to='pictures/productcategory/', blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.type_of_product

    # def save(self, *args, **kwargs):
    #     return super(ProductCategory, self).save(*args, **kwargs)


class ProductMeta(BaseModel): # Prodect Meta (original product name with comapny name)
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to="pictures/productmeta/", blank=True, null=True)
    product_category = models.ForeignKey(ProductCategory,on_delete=models.CASCADE)
    shop_category = models.ForeignKey(ShopCategory,on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Product(BaseModel):
    product_name = models.CharField(max_length=100, blank=True, null=True)
    product_image = models.ImageField(upload_to='pictures/product/', blank=False, null=False)
    # product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE)
    product_price = models.DecimalField(decimal_places=2,max_digits=7,blank=True, null=True)
    product_meta = models.ForeignKey(ProductMeta, on_delete=models.CASCADE)
    history = HistoricalRecords()
    product_last_price = models.DecimalField(decimal_places=2,max_digits=7,blank=True,null=True,default=0.00)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name




