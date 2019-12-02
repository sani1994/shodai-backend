from datetime import datetime
import random

from django.db import models
from simple_history.models import HistoricalRecords

from order.models import Order
from product.models import ProductCategory, Product
from userProfile.models import Address, UserProfile
from bases.models import BaseModel
from django.contrib.gis.db import models
# Create your models here.
from utility.models import ProductUnit


class ProducerBulkRequest(BaseModel):  # producer product
    '''
    This is the model for Producer Bulk Request
    '''
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=200, null=False, blank=False)
    product_image = models.ImageField(upload_to='producer/product', null=True, blank=True)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, related_name='producer_unit', null=True, blank=True)
    production_time = models.DateTimeField(null=True, blank=True)
    unit_price = models.FloatField(null=False, blank=False)
    quantity = models.FloatField(blank=True, null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)
    general_price = models.FloatField(null=True, blank=True)
    general_qty = models.FloatField(blank=True, null=True)
    general_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, related_name='general_unit', blank=True,
                                     null=True)
    offer_price = models.FloatField(null=True, blank=True)
    offer_qty = models.FloatField(blank=True, null=True)
    offer_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, related_name='offer_unit', blank=True,
                                   null=True)
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REQUEST_STATUS = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
    ]
    status = models.CharField(choices=REQUEST_STATUS, default=PENDING, max_length=20)

    def __str__(self):
        return self.product_name

    def productlistforcustomer(self):
        bulk_order_products = self.bulkorderproducts_set.all()
        print(bulk_order_products)
        micro_bulk_order_products =bulk_order_products.microbulkorderproducts_set.all()
        print(micro_bulk_order_products)
        return micro_bulk_order_products.customermicroBulkorderproductrequest_set.all().count()
        # return bulk_order_products

    def save(self, *args, **kwargs):
        if self.is_approved:
            self.status = self.ACCEPTED
        return super(ProducerBulkRequest, self).save(*args, **kwargs)


class BusinessType(BaseModel):
    '''
    This Model defines the business types of the Producer
    '''
    business_type = models.CharField(max_length=100)
    history = HistoricalRecords()

    def __str__(self):
        return self.business_type


class ProducerBusiness(BaseModel):
    '''
    This is the model for Producer Business location and other relevant details like contact and approval status
    '''
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    business_image = models.ImageField(upload_to='producer/business', blank=True, null=True)
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE)
    total_employees = models.IntegerField(null=True, blank=True)
    land_amount = models.CharField(max_length=30, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    productbusiness_geopoint = models.PointField(null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name

    def save(self, *args, **kwargs):
        self.productbusiness_geopoint.y = self.lat
        self.productbusiness_geopoint.x = self.long
        super(ProducerBusiness, self).save(*args, **kwargs)


class ProducerFarm(BaseModel):
    '''
    This is the model for Producer Farm related info and location
    '''
    land_amount = models.CharField(max_length=30, blank=True, null=True)
    type_of_crops_produce = models.CharField(max_length=30, blank=True, null=True)
    product_photo = models.ImageField(blank=True, null=True)
    address = models.ForeignKey(Address, models.SET_NULL, blank=True, null=True)
    history = HistoricalRecords()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.type_of_crops_produce


class BulkOrder(BaseModel):
    '''
    This is the model for Bulk Order for Producer's Produce created by Shodai
    this will have limited time
    '''
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    expire_date = models.DateTimeField(blank=False, null=False)
    start_date = models.DateTimeField(auto_now=True)
    hex_code = models.CharField(max_length=20, default=None, unique=True, null=True, blank=True)

    def __str__(self):
        return self.user.username

    # def save(self, *args, **kwargs):
    #     if not self.hex_code:
    #         now = datetime.now()
    #         self.hex_code=hex(now)
    #     return super(BulkOrder, self).save(*args, **kwargs)




class BulkOrderProducts(BaseModel):
    '''
    This is the model for the Products against the Bulk Order for Producer
    '''
    product = models.ForeignKey(ProducerBulkRequest, on_delete=models.CASCADE, related_name='bulk_order_products')
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE, related_name='bulk_orders_products')
    general_price = models.FloatField(blank=True, null=True)
    offer_price = models.FloatField(blank=True, null=True)
    target_qty = models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=5)
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.product.product_name


class MicroBulkOrder(BaseModel):
    '''
    This is the model for Micro Bulk Order which is going to be created against the Bulk Order for Producer's produce
    '''
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE, related_name='micro_bulk_order')
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.customer.first_name


class MicroBulkOrderProducts(BaseModel):  # micro_bulk_order=mco
    '''
    This is the model for the Products against the Micro Bulk Order
    '''
    bulk_order_products = models.ForeignKey(BulkOrderProducts, on_delete=models.CASCADE, null=True, blank=True)
    micro_bulk_order = models.ForeignKey(MicroBulkOrder, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='mcop')
    qty = models.FloatField(default=0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    # def __str__(self):
    #     pass
        # return self.order.user.first_name


class BulkOrderReqConnector(BaseModel):
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE)
    producer_bulk_request = models.ForeignKey(ProducerBulkRequest, on_delete=models.CASCADE)


class CustomerMicroBulkOrderProductRequest(
    BaseModel):  # customer will input qty request against MicrobulkorderRest obj. #newly added
    '''
    This is the model for the Customer's Orders of Products against the Micro Bulk Order Products
    But I think this should be part of MicroBulkOrderProducts.
    '''
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    micro_bulk_order_product = models.ForeignKey(MicroBulkOrderProducts, on_delete=models.CASCADE,related_name='cmbopr') # CustomerMicroBulkOrderProductRequest = cmbopr
    qty = models.FloatField(default=0.0)
    shareable_ref_code = models.CharField(max_length=100, default=None,
                                          unique=True)  # code that will share to the next customer
    accepted_ref_code = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.customer.first_name

    def save(self, *args, **kwargs):
        if self.shareable_ref_code is None:
            # time = datetime.now(tz=None)
            unique_code = hex(int(self.customer.mobile_number)) + str(datetime.now())
            self.shareable_ref_code = unique_code
        return super(CustomerMicroBulkOrderProductRequest, self).save(*args, **kwargs)
