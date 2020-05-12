import uuid
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from django.contrib.gis.geos import GEOSGeometry
from userProfile.models import UserProfile
from product.models import ProductMeta
from product.models import Product
from bases.models import BaseModel
from userProfile.models import Address


# Create your models here.


class Order(BaseModel):
    user = models.ForeignKey(UserProfile, models.SET_NULL, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, unique=True)
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=100, null=True, blank=True, unique=True,)
    bill_id = models.CharField(max_length=100, null=True, blank=True, unique=True,)
    currency = models.CharField(max_length=3, blank=True, default='BDT')
    delivery_date_time = models.DateTimeField(auto_now=True)
    delivery_place = models.CharField(max_length=100)
    order_total_price = models.FloatField(default=0)
    lat = models.FloatField()
    long = models.FloatField()
    order_geopoint = models.PointField(null=True, blank=True)

    ORDERED = 'OD'  # ORDER COLLECT FROM CUSTOMER
    ORDER_ACCEPTED = 'OA'  # ORDER ACCEPTED BY RETAILER OR PRODUCER
    ORDER_READY = 'RE'  # ORDER IS READY FOR DELIVERY PERSON
    ORDER_AT_DELIVERY = 'OAD'  # ORDER IS WITH DELIVERY PEROSN
    ORDER_COMPLETED = 'COM'  # ORDER IS DELIVERED TO CUSTOMER
    ORDER_CANCELLED = 'CN'  # ORDER IS CANCEL BY CUSTOMER
    ORDER_STATUS = [
        (ORDERED, 'Ordered'),
        (ORDER_ACCEPTED, 'Order Accepted'),
        (ORDER_READY, 'Order Ready'),
        (ORDER_AT_DELIVERY, 'Order At Delivery'),
        (ORDER_COMPLETED, 'Order Completed'),
        (ORDER_CANCELLED, 'Order Cancelled'),
    ]
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default=ORDERED)
    home_delivery = models.BooleanField(default=True, null=False, blank=False)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)

    FIXED_PRICE = 'FP'
    BIDDING = 'BD'
    ORDER_TYPES = [
        (FIXED_PRICE, 'Fixed Price'),
        (BIDDING, 'Biding'),
    ]
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default=FIXED_PRICE)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return "{}".format(self.id)

    # def __int__(self):
    #     return self.order_id

    # @property
    # def order_count(self): # saikat
    #     count = self.orders.count()
    #     # print(count)
    #     return count

    @property
    def products(self):
        order_product = self.orders.all()
        return order_product

    def save(self, *args, **kwargs):
        # self.shop_geopoint.y = self.shop_lat
        # self.shop_geopoint.x = self.shop_long
        # self.shop_geopoint = GEOSGeometry('POINT (' + self.shop_long + self.shop_lat + ')')
        self.payment_id = str(uuid.uuid4())[:8]
        self.invoice_number = str(uuid.uuid4())[:8]
        self.bill_id = str(uuid.uuid4())[:8]
        self.currency = 'BDT'

        # self.delivery_date_time = self.delivery_date_time.strftime("%Y-%m-%d %H:%M%p")

        self.order_geopoint = GEOSGeometry('POINT(%f %f)' % (self.long, self.lat))
        super(Order, self).save(*args, **kwargs)


class OrderProduct(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='orders', on_delete=models.CASCADE)
    order_product_id = models.CharField(max_length=100, blank=True, null=True, unique=True, )  # new
    order_product_price = models.FloatField(blank=False, null=False,
                                            default=0)  # product may belong to offer do the price
    order_product_qty = models.FloatField(default=1)
    history = HistoricalRecords()

    def __str__(self):
        return self.product.product_name

    def save(self, *args, **kwargs):  # new
        self.order_product_id = str(uuid.uuid4())[:8]
        super(OrderProduct, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order Product'
        verbose_name_plural = 'Order Product'


class Vat(BaseModel):
    product_meta = models.ForeignKey(ProductMeta, on_delete=models.CASCADE, blank=True, null=True, default=None)
    vat_amount = models.FloatField(default=0, blank=False, null=False, verbose_name='Vat Amount(%)')
    history = HistoricalRecords()

    def __str__(self):
        return str(self.vat_amount)


class DeliveryCharge(BaseModel):
    delivery_charge_inside_dhaka = models.FloatField(default=0, verbose_name='Delivery Charge(Dhaka)')
    delivery_charge_outside_dhaka = models.FloatField(default=0, verbose_name='Delivery Charge(Outside)')

    def __str__(self):
        return '{}'.format(str(self.delivery_charge_inside_dhaka))


####### 
# q= str(uuid.uuid4())[:8]
# print(q)
# models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class PaymentInfo(models.Model):
    """PaymentInfo object"""
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    order_id = models.CharField(max_length=20, null=True, blank=True)
    bill_id = models.CharField(max_length=100, null=True, blank=True)
    create_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order_id) + " " + str(self.payment_id)

class TransactionId(models.Model):
    transaction_id = models.CharField(max_length=100, null=True, blank=True,)
    create_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.transaction_id)