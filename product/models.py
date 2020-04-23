from django.db import models
from simple_history.models import HistoricalRecords
from bases.models import BaseModel
from django.db.models.signals import pre_save
# Create your models here.
from utility.models import ProductUnit


class ShopCategory(BaseModel):
    type_of_shop = models.CharField(max_length=89)
    type_of_shop_bn = models.CharField(max_length=90,null=True,blank=True,verbose_name='দোকানের ধরন')
    history = HistoricalRecords()

    def __str__(self):
        return self.type_of_shop

    class Meta:
        verbose_name = 'Shop Category'
        verbose_name_plural = 'Shop Category'


class ProductCategory(BaseModel):
    type_of_product = models.CharField(max_length=90)
    type_of_product_bn = models.CharField(max_length=90,null=True,blank=True,verbose_name='পন্যের ধরন')
    img = models.ImageField(upload_to='pictures/productcategory/', blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.type_of_product

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Category'


class ProductMeta(BaseModel): # Prodect Meta (original product name with comapny name)
    name = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100,null=True,blank=True,verbose_name='নাম')
    img = models.ImageField(upload_to="pictures/productmeta/", blank=True, null=True)
    product_category = models.ForeignKey(ProductCategory,on_delete=models.CASCADE)
    shop_category = models.ForeignKey(ShopCategory,on_delete=models.CASCADE,verbose_name='Product Type')
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product Meta'
        verbose_name_plural = 'Product Meta'


class Product(BaseModel):
    product_name = models.CharField(max_length=100, blank=True, null=True)
    product_name_bn = models.CharField(max_length=100,null=True,blank=True,verbose_name= 'পন্যের নাম')
    product_image = models.ImageField(upload_to='pictures/product/', blank=False, null=False)
    product_description = models.CharField(max_length=200,default=" ")
    product_description_bn = models.CharField(max_length=200, default=" ")
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE,default=None)
    product_price = models.DecimalField(decimal_places=2,max_digits=7,blank=True, null=True)
    product_price_bn = models.DecimalField(decimal_places=2,max_digits=7,blank=True,null=True,verbose_name='পন্যের মুল্য')
    product_meta = models.ForeignKey(ProductMeta, on_delete=models.CASCADE)
    product_last_price = models.DecimalField(decimal_places=2,max_digits=7,default=0.00)
    is_approved = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.product_name

    @property
    def product_unit_name(self):
        return self.product_unit.product_unit

    def product_meta_name(self):
        return self.product_meta.name

