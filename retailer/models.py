from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from simple_history.models import HistoricalRecords
from product.models import ShopCategory, Product, ProductMeta
from userProfile.models import UserProfile
from userProfile.models import Address
from order.models import Order, OrderProduct
from bases.models import BaseModel
# from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db import models as gis_models
from utility.models import ProductUnit


# Create your models here.


class Account(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    account_no = models.CharField(max_length=100, blank=True, null=True)
    account_name = models.CharField(max_length=50, blank=True, null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Shop(BaseModel):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    # shodai_products = models.ManyToManyField(Product)
    shop_name = models.CharField(max_length=100, null=False, blank=False)
    shop_type = models.ForeignKey(ShopCategory, on_delete=models.CASCADE)
    shop_lat = models.FloatField(null=True, blank=True)
    shop_long = models.FloatField(null=True, blank=True)
    shop_geopoint = gis_models.PointField(null=True)
    shop_address = models.CharField(max_length=100, blank=True, null=True)
    shop_image = models.ImageField(upload_to='retailer/shop/%Y/%m/%d', null=True, blank=True)
    shop_licence = models.CharField(max_length=200, blank=True, null=True, unique=True)  # trade licence
    shop_website = models.CharField(max_length=100, blank=True, null=True)
    shop_open_time = models.TimeField(auto_now=False, null=True)
    shop_close_time = models.TimeField(auto_now=False, null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    # geo_objects = gis_models.GeoManager()

    def __str__(self):
        return self.shop_name

    def save(self, *args, **kwargs):
        # self.shop_geopoint.y = self.shop_lat
        # self.shop_geopoint.x = self.shop_long
        # self.shop_geopoint = GEOSGeometry('POINT (' + self.shop_long + self.shop_lat + ')')
        self.shop_geopoint = GEOSGeometry('POINT(%f %f)' % (self.shop_long, self.shop_lat))
        super(Shop, self).save(*args, **kwargs)


class AcceptedOrder(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True,
                             null=True)  # to track the order by shop, shop has been added as a foreign key
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_product = models.ForeignKey(OrderProduct, on_delete=models.CASCADE, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.user.username


class ShopProduct(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='retailer', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Shodai Product')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True, null=True)
    # product_image = models.ImageField(upload_to='pictures/product/', blank=False, null=False)
    product_image = models.CharField(max_length=255, blank=True, null=True)
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE)
    product_price = models.DecimalField(decimal_places=2, max_digits=7, blank=True, null=True)
    product_stock = models.DecimalField(decimal_places=2, max_digits=7, blank=True, null=True)
    history = HistoricalRecords()
    product_last_price = models.DecimalField(decimal_places=2, max_digits=7, blank=True, null=True, default=0.00)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return str(self.product.id) + self.product.product_name

    def save(self, *args, **kwargs):
        if not self.product_image:
            self.product_image = self.product.product_image.url

        if not self.product_price:
            self.product_price = self.product.product_price

        return super(ShopProduct, self).save(*args, **kwargs)

    @property
    def product_name(self):
        # product_name = self.product.product_name
        # product_name_bn = self.product.product_name_bn

        # product = [
        #     product_name,
        #     product_name_bn
        # ]
        return self.product.product_name

    @property
    def product_name_bn(self):

        return self.product.product_name_bn

    @property
    def product_description(self):

        return self.product.product_description

    @property
    def product_description_bn(self):

        return self.product.product_description_bn

    @property
    def product_unit_name(self):

        return self.product_unit.product_unit
