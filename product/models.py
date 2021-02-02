from django.db import models
from django.utils.text import slugify
from simple_history.models import HistoricalRecords
from bases.models import BaseModel
from utility.models import ProductUnit


class ShopCategory(BaseModel):
    type_of_shop = models.CharField(max_length=89)
    type_of_shop_bn = models.CharField(max_length=90, null=True, blank=True, verbose_name='দোকানের ধরন')
    is_approved = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.type_of_shop

    class Meta:
        verbose_name = 'Shop Category'
        verbose_name_plural = 'Shop Category'


class ProductCategory(BaseModel):
    type_of_product = models.CharField(max_length=90)
    type_of_product_bn = models.CharField(max_length=90, null=True, blank=True, verbose_name='পন্যের ধরন')
    img = models.ImageField(upload_to='pictures/productcategory/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.type_of_product

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Category'


class ProductMeta(BaseModel):  # Prodect Meta (original product name with comapny name)
    name = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100, null=True, blank=True, verbose_name='নাম')
    img = models.ImageField(upload_to="pictures/productmeta/", blank=True, null=True)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    shop_category = models.ForeignKey(ShopCategory, on_delete=models.CASCADE, verbose_name='Product Type')
    vat_amount = models.FloatField(default=0, blank=True, null=True,
                                   verbose_name='Vat Amount(%)')  # Here vat amount 15 is 15%
    is_approved = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product Meta'
        verbose_name_plural = 'Product Meta'


class Product(BaseModel):
    product_name = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    product_name_bn = models.CharField(max_length=100, null=True, blank=True, verbose_name='পন্যের নাম')
    product_image = models.ImageField(upload_to='pictures/product/', blank=False, null=False)
    product_description = models.CharField(max_length=400, default=" ")
    product_description_bn = models.CharField(max_length=400, default=" ")
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, default=None)
    product_price = models.DecimalField(decimal_places=2, max_digits=7, blank=True, null=True)
    product_price_bn = models.DecimalField(decimal_places=2, max_digits=7, blank=True, null=True,
                                           verbose_name='পন্যের মুল্য')
    product_meta = models.ForeignKey(ProductMeta, on_delete=models.CASCADE)
    product_last_price = models.DecimalField(decimal_places=2, max_digits=7, default=0.00)
    is_approved = models.BooleanField(default=False)
    decimal_allowed = models.BooleanField(default=False)
    price_with_vat = models.DecimalField(decimal_places=2, max_digits=7, default=0.00, blank=True, null=True,
                                         verbose_name='Product Price With Vat')  # Product Price with vat
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        """calculte price_with_vat using vat field from product meta object"""
        if self.product_meta.vat_amount:
            price = float(self.product_price) + (float(self.product_price) * self.product_meta.vat_amount) / 100
            self.price_with_vat = round(price)
            super(Product, self).save(*args, **kwargs)
        else:
            self.price_with_vat = self.product_price

        self.slug = slugify(self.product_name) + "-" + slugify(self.product_unit.product_unit)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name + " " + self.product_unit.product_unit + " (price: " + str(self.product_price) + ")"

    @property
    def product_price_with_vat(self):
        if self.product_meta.vat_amount:
            return float(self.product_price) + (float(self.product_price) * self.product_meta.vat_amount) / 100
        return self.product_price

    @property
    def vat_amount(self):
        if self.product_meta.vat_amount:
            return (self.product_price * self.product_meta.vat_amount) / 100
        return 0.0

    @property
    def product_unit_name(self):
        return self.product_unit.product_unit

    @property
    def product_meta_name(self):
        return self.product_meta.name

    @property
    def product_category_name(self):
        return self.product_meta.product_category.type_of_product
