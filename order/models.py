import uuid
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from django.contrib.gis.geos import GEOSGeometry
from django.utils.translation import ugettext_lazy as _
from userProfile.models import UserProfile
from product.models import ProductMeta
from product.models import Product
from bases.models import BaseModel
from userProfile.models import Address


# Create your models here.


class Order(BaseModel):
    """Create order object"""
    user = models.ForeignKey(UserProfile, models.SET_NULL, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, unique=True, )
    invoice_number = models.CharField(max_length=100, null=True, blank=True, unique=True, )
    bill_id = models.CharField(max_length=100, null=True, blank=True, unique=True, )
    currency = models.CharField(max_length=3, blank=True, default='BDT')
    delivery_date_time = models.DateTimeField()
    delivery_place = models.CharField(max_length=100)
    order_total_price = models.FloatField(default=0)  # storing price+vat+delivery_charge
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

    @property
    def products(self):
        order_product = self.orders.all()
        return order_product

    @property
    def paid_status(self):
        status = InvoiceInfo.objects.get(order_number_id=self.id).paid_status
        if status==True:
            return 'Paid Status'
        else:
            return 'Not Paid Status'
        return 'Not Paid Status'

    def save(self, *args, **kwargs):
        # self.shop_geopoint.y = self.shop_lat
        # self.shop_geopoint.x = self.shop_long
        # self.shop_geopoint = GEOSGeometry('POINT (' + self.shop_long + self.shop_lat + ')')
        self.payment_id = str(uuid.uuid4())[:8]
        self.invoice_number = str(uuid.uuid4())[:8]
        self.bill_id = str(uuid.uuid4())[:8]
        self.currency = 'BDT'
        self.order_geopoint = GEOSGeometry('POINT(%f %f)' % (self.long, self.lat))
        super(Order, self).save(*args, **kwargs)

    @property
    def order_product_name(self):
        orders = OrderProduct.objects.filter(order=self)
        order_product_detail = []
        [order_product_detail.append(op.product.product_name + "\n") for op in orders]
        order_product = f"{''.join(order_product_detail)}"
        return order_product

    @property
    def order_product_unit(self):
        orders = OrderProduct.objects.filter(order=self)
        order_product_detail = []
        [order_product_detail.append(op.product.product_unit.product_unit + "\n") for op in orders]
        order_product = f"{''.join(order_product_detail)}"
        return order_product

    @property
    def order_product_quantity(self):
        orders = OrderProduct.objects.filter(order=self)
        order_product_detail = []
        [order_product_detail.append(str(op.order_product_qty) + "\n") for op in orders]
        order_product = f"{''.join(order_product_detail)}"
        return order_product


class OrderProduct(BaseModel):
    """Create order product object"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='orders', on_delete=models.CASCADE)
    order_product_price = models.FloatField(blank=False, null=False,
                                            default=0)  # product may belong to offer do the price
    order_product_price_with_vat = models.FloatField(blank=False, null=False,
                                                     default=0)  # added to track price with vat
    vat_amount = models.FloatField(default=0, blank=True, null=True,
                                   verbose_name='Vat Amount(%)')  # Here vat amount 15 is 15%; added to track vat
    order_product_qty = models.FloatField(default=1)
    history = HistoricalRecords()

    def __str__(self):
        return self.product.product_name

    def save(self, *args, **kwargs):
        """Save order_product_price_with_vat field using price_with_vat from product object.
           Save order_product_price_with_vat field using price_with_vat from product object
        """
        self.order_product_price_with_vat = self.product.price_with_vat
        self.vat_amount = self.product.product_meta.vat_amount
        super(OrderProduct, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order Product'
        verbose_name_plural = 'Order Product'

    @property
    def order_product_unit(self):
        order_product_unit = self.product.product_unit.product_unit
        return order_product_unit


class Vat(BaseModel):
    """Vat object (now not needed)"""
    product_meta = models.ForeignKey(ProductMeta, on_delete=models.CASCADE, blank=True, null=True, default=None)
    vat_amount = models.FloatField(default=0, blank=False, null=False, verbose_name='Vat Amount(%)')
    history = HistoricalRecords()

    def __str__(self):
        return str(self.vat_amount)


class DeliveryCharge(BaseModel):
    """Delivery Charge object"""
    delivery_charge_inside_dhaka = models.FloatField(default=0, verbose_name='Delivery Charge(Dhaka)')
    delivery_charge_outside_dhaka = models.FloatField(default=0, verbose_name='Delivery Charge(Outside)')

    def __str__(self):
        return '{}'.format(str(self.delivery_charge_inside_dhaka))


class PaymentInfo(models.Model):
    """PaymentInfo object"""
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'
    INITIATED = 'INITIATED'
    PAYMENT_STATUS = [
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
        (CANCELLED, 'Cancelled'),
        (INITIATED, 'Initiated')
    ]
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    order_id = models.ForeignKey(Order, related_name='payment', on_delete=models.CASCADE, blank=True, null=True)
    bill_id = models.CharField(max_length=100, null=True, blank=True)
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default=INITIATED)
    create_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'OrderId: ' + str(self.order_id) + "  " + "PaymentId: " + str(self.payment_id)


class TimeSlot(models.Model):
    start = models.CharField(max_length=10)
    end = models.CharField(max_length=10)
    time = models.TimeField()
    allow = models.BooleanField(default=True)
    slot = models.CharField(max_length=100, blank=True, null=True, help_text=_("Auto Save"))

    def __str__(self):
        return self.start + '-' + self.end

    def save(self, *args, **kwargs):
        self.slot = self.start + '-' + self.end
        super(TimeSlot, self).save(*args, **kwargs)


class InvoiceInfo(BaseModel):
    invoice_number = models.CharField(max_length=100, unique=True, null=False, blank=False, default="")
    billing_person_name = models.CharField(max_length=50, null=True, blank=True)
    billing_person_email = models.EmailField(blank=True, null=True)
    billing_person_mobile_number = models.CharField(max_length=20, null=True, blank=True)
    delivery_contact_number = models.CharField(max_length=20, null=True, blank=True)
    delivery_address = models.CharField(max_length=200)
    delivery_date_time = models.DateTimeField()
    delivery_charge = models.FloatField(default=0)
    discount_amount = models.FloatField(null=True, blank=True)
    discount_description = models.CharField(max_length=100, null=True, blank=True)
    net_payable_amount = models.FloatField(default=0, null=False, blank=False)
    paid_status = models.BooleanField(default=False, null=False, blank=False)
    ONLINE_PAYMENT = 'SSLCOMMERZ'
    CASH_ON_DELIVERY = 'COD'
    PAYMENT_METHOD = [
        (ONLINE_PAYMENT, 'SSLCommerz'),
        (CASH_ON_DELIVERY, 'Cod'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default=CASH_ON_DELIVERY)
    currency = models.CharField(max_length=3, blank=True, default='BDT')
    order_number = models.ForeignKey(Order, related_name='invoice', blank=True, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, models.SET_NULL, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return 'OrderId: ' + str(self.order_number) + "  " + "InvoiceNumber: " + str(self.invoice_number)
