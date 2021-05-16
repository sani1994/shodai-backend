import random
from datetime import datetime
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from ckeditor_uploader.fields import RichTextUploadingField
from simple_history.models import HistoricalRecords

from product.models import ProductCategory
from user.models import Address, UserProfile
from base.models import BaseModel
from utility.models import ProductUnit


class ProducerProductRequest(BaseModel):
    """
    This is the model for Producer Product Request
    """
    product_name = models.CharField(max_length=200)
    product_image = models.ImageField(upload_to='pictures/producer/product')
    product_description = RichTextUploadingField()
    product_unit = models.CharField(max_length=20)
    product_price = models.FloatField()
    product_quantity = models.FloatField()
    producer = models.ForeignKey(UserProfile, models.SET_NULL, null=True)
    is_approved = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.product_name


class ProducerBulkRequest(BaseModel):  # producer product
    """
    This is the model for Producer Bulk Request
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=200, null=False, blank=False)
    product_name_bn = models.CharField(max_length=100, null=True, blank=True,
                                       verbose_name='পন্যের নাম')
    product_image = models.ImageField(upload_to='producer/product', null=True, blank=True)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE,
                             related_name='producer_unit',
                             null=True,
                             blank=True)
    production_time = models.DateTimeField(null=True, blank=True)
    unit_price = models.FloatField(null=False, blank=False)
    quantity = models.FloatField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    general_price = models.FloatField(null=True, blank=True)
    general_qty = models.FloatField(blank=True, null=True)
    general_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE,
                                     related_name='general_unit',
                                     blank=True, null=True
                                     )
    offer_price = models.FloatField(null=True, blank=True)
    offer_qty = models.FloatField(blank=True, null=True)
    offer_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE,
                                   related_name='offer_unit',
                                   blank=True,
                                   null=True)
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REQUEST_STATUS = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
    ]
    status = models.CharField(choices=REQUEST_STATUS, default=PENDING, max_length=20)
    history = HistoricalRecords()

    def __str__(self):
        return self.product_name

    # def productlistforcustomer(self):
    #     bulk_order_products = self.bulkorderproducts_set.all()
    #     micro_bulk_order_products =bulk_order_products.microbulkorderproducts_set.all()
    #     return micro_bulk_order_products.customermicroBulkorderproductrequest_set.all().count()
    #     # return bulk_order_products

    def save(self, *args, **kwargs):
        if self.is_approved:
            self.status = self.ACCEPTED
        return super(ProducerBulkRequest, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Producer Bulk Request"
        verbose_name = "producer product"


class BusinessType(BaseModel):
    """
    This Model defines the business types of the Producer
    """
    business_type = models.CharField(max_length=100)
    history = HistoricalRecords()

    def __str__(self):
        return self.business_type


class ProducerBusiness(BaseModel):
    """
    This is the model for Producer Business location and other relevant details like contact and approval status
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    business_image = models.ImageField(upload_to='producer/business', blank=True, null=True)
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE)
    total_employees = models.IntegerField(null=True, blank=True)
    land_amount = models.CharField(max_length=30, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    product_business_geopoint = models.PointField(null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.user.first_name

    def save(self, *args, **kwargs):
        self.productbusiness_geopoint = Point(self.long, self.lat)
        super(ProducerBusiness, self).save(*args, **kwargs)


class ProducerFarm(BaseModel):
    """
    This is the model for Producer Farm related info and location
    """
    land_amount = models.CharField(max_length=30, blank=True, null=True)
    type_of_crops_produce = models.CharField(max_length=30, blank=True, null=True)
    product_photo = models.ImageField(blank=True, null=True)
    address = models.ForeignKey(Address, models.SET_NULL, blank=True, null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.type_of_crops_produce


class BulkOrder(BaseModel):
    """
    This is the model for Bulk Order for Producer's Produce created by Shodai
    this will have limited time
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField(blank=False, null=False)
    expire_date = models.DateTimeField(blank=False, null=False)
    hex_code = models.CharField(max_length=20, default=None, unique=True, null=True, blank=True)

    def __str__(self):
        return self.user.username

    # def save(self, *args, **kwargs):
    #     if not self.hex_code:
    #         now = datetime.now()
    #         self.hex_code=hex(now)
    #     return super(BulkOrder, self).save(*args, **kwargs)


class BulkOrderProducts(BaseModel):
    """
    This is the model for the Products against the Bulk Order for Producer
    """
    product = models.ForeignKey(ProducerBulkRequest, on_delete=models.CASCADE, related_name='bulk_order_products')
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE, related_name='bulk_orders_products')
    general_price = models.FloatField(blank=True, null=True)
    offer_price = models.FloatField(blank=True, null=True)
    target_qty = models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=5)
    max_qty = models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=5)
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, blank=True, null=True)
    shareable_ref_code = models.CharField(max_length=100, null=True, blank=True,
                                          unique=True)  # code that will share to the next customer
    available_qty = models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=5)

    def __str__(self):
        return self.product.product_name

    def save(self, *args, **kwargs):
        if self.shareable_ref_code is None:
            # time = datetime.now(tz=None)
            unique_code = hex(int(random.randint(10, 99))) + str(datetime.now())
            self.shareable_ref_code = hex(int(datetime.timestamp(datetime.now())))
        if not self.id:
            self.available_qty = self.target_qty
        return super(BulkOrderProducts, self).save(*args, **kwargs)


class MicroBulkOrder(BaseModel):
    """
    This is the model for Micro Bulk Order which is going to be created against the Bulk Order for Producer's produce
    """
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE, related_name='micro_bulk_order')
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True)
    # shareable_ref_code = models.CharField(max_length=100,null=True,blank=True,
    #                                       unique=True)  # code that will share to the next customer
    accepted_ref_code = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.id)

    # def save(self, *args, **kwargs):
    #     if self.shareable_ref_code is None:
    #         # time = datetime.now(tz=None)
    #         unique_code = hex(int(self.customer.mobile_number)) + str(datetime.now())
    #         self.shareable_ref_code = unique_code
    #     return super(MicroBulkOrder, self).save(*args, **kwargs)


class MicroBulkOrderProducts(BaseModel):  # micro_bulk_order=mco
    """
    This is the model for the Products against the Micro Bulk Order
    """
    bulk_order_products = models.ForeignKey(BulkOrderProducts, on_delete=models.CASCADE, null=True)
    micro_bulk_order = models.ForeignKey(MicroBulkOrder, on_delete=models.CASCADE, null=True)
    qty = models.DecimalField(decimal_places=2, default=0, max_digits=5)
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.bulk_order_products:
            return '{}'.format(self.bulk_order_products.product)
        else:
            return '{}'.format(str(self.id))


class BulkOrderReqConnector(BaseModel):
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE)
    producer_bulk_request = models.ForeignKey(ProducerBulkRequest, on_delete=models.CASCADE)

    def __str__(self):
        return self.producer_bulk_request.product_name
