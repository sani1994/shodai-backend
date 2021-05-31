from django.contrib.gis.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from django.utils.translation import ugettext_lazy as _

from coupon.models import CouponCode
from offer.models import OfferProduct, Offer
from producer.models import ProducerProductRequest
from user.models import UserProfile, Address
from product.models import ProductMeta
from product.models import Product
from base.models import BaseModel


# Create your models here.


class Order(BaseModel):
    """Create order object"""
    user = models.ForeignKey(UserProfile, models.SET_NULL, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, )
    invoice_number = models.CharField(max_length=100, null=True, blank=True, unique=True)
    order_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    bill_id = models.CharField(max_length=100, null=True, blank=True, unique=True, )
    currency = models.CharField(max_length=3, blank=True, default='BDT')
    delivery_date_time = models.DateTimeField()
    placed_on = models.DateTimeField(default=timezone.now)
    delivery_place = models.CharField(max_length=100)
    total_vat = models.FloatField(default=0)  # storing total vat on products
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
        (ORDER_AT_DELIVERY, 'Order at Delivery'),
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
    note = models.CharField(max_length=500, null=True, blank=True, default="")
    remarks = models.CharField(max_length=500, null=True, blank=True, default="")
    WEBSITE = 'WB'
    ADMIN_PANEL = 'AD'
    MOBILE_APPLICATION = 'AP'
    PLATFORM = [
        (WEBSITE, 'Website'),
        (ADMIN_PANEL, 'Admin Panel'),
        (MOBILE_APPLICATION, 'Mobile Application')
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM, default=WEBSITE)
    history = HistoricalRecords()

    def __str__(self):
        return "{}".format(self.id)

    @property
    def products(self):
        order_product = self.orders.all()
        return order_product

    @property
    def paid_status(self):
        invoice = InvoiceInfo.objects.filter(order_number=self).order_by('-created_on')
        if invoice and invoice[0].paid_status:
            return 'Paid'
        else:
            return 'Not Paid'

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
    product_price = models.FloatField(blank=False, null=False, default=0)
    history = HistoricalRecords()

    def __str__(self):
        return self.product.product_name

    def save(self, *args, **kwargs):
        """Save order_product_price_with_vat field using price_with_vat from product object.
           Save order_product_price_with_vat field using price_with_vat from product object
        """
        if not self.order_product_price:
            today = timezone.now()
            offer_product = OfferProduct.objects.filter(is_approved=True, offer__offer_starts_in__lte=today,
                                                        offer__offer_ends_in__gte=today, product=self.product)

            if offer_product.exists():
                self.order_product_price = float(offer_product[0].offer_price)
            else:
                self.order_product_price = float(self.product.product_price)
            self.product_price = self.product.product_price
        self.vat_amount = self.product.product_meta.vat_amount
        self.order_product_price_with_vat = round(self.order_product_price +
                                                  (self.order_product_price * self.vat_amount) / 100)
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
    discount_amount = models.FloatField(default=0, null=True, blank=True)
    discount_description = models.CharField(max_length=500, null=True, blank=True)
    net_payable_amount = models.FloatField(default=0, null=False, blank=False)
    paid_status = models.BooleanField(default=False, null=False, blank=False)
    paid_on = models.DateTimeField(null=True, blank=True)
    ONLINE_PAYMENT = 'SSLCOMMERZ'
    CASH_ON_DELIVERY = 'CASH_ON_DELIVERY'
    PAYMENT_METHOD = [
        (ONLINE_PAYMENT, 'SSLCommerz'),
        (CASH_ON_DELIVERY, 'Cash on Delivery'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default=CASH_ON_DELIVERY)
    currency = models.CharField(max_length=3, blank=True, default='BDT')
    order_number = models.ForeignKey(Order, related_name='invoice', blank=True, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, models.SET_NULL, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return 'Order Number: {} Invoice Number: {}'.format(self.order_number.order_number,
                                                            self.invoice_number)


class DiscountInfo(BaseModel):
    COUPON_DISCOUNT = 'CP'
    PRODUCT_DISCOUNT = 'PD'
    DELIVERY_CHARGE_DISCOUNT = 'DC'
    ADDITIONAL_DISCOUNT = 'AD'
    DISCOUNT_TYPE = [
        (COUPON_DISCOUNT, 'Coupon Discount'),
        (PRODUCT_DISCOUNT, 'Product Discount'),
        (DELIVERY_CHARGE_DISCOUNT, 'Delivery Charge Discount'),
        (ADDITIONAL_DISCOUNT, 'Additional Discount')
    ]
    discount_amount = models.FloatField(default=0, blank=True, null=True, )
    discount_type = models.CharField(max_length=30, choices=DISCOUNT_TYPE, default=PRODUCT_DISCOUNT)
    discount_description = models.CharField(max_length=500, null=True, blank=True)
    coupon = models.ForeignKey(CouponCode, models.SET_NULL, null=True)
    offer = models.ForeignKey(Offer, models.SET_NULL, null=True)
    invoice = models.ForeignKey(InvoiceInfo, models.CASCADE, related_name='discounts')

    def __str__(self):
        return str(self.id) + " - " + "InvoiceNumber: " + str(self.invoice.invoice_number)


class PreOrderSetting(BaseModel):
    """
    This is the model for Pre Order for Producer's Product
    """
    producer_product = models.OneToOneField(ProducerProductRequest, models.CASCADE)
    product = models.ForeignKey(Product, models.CASCADE)
    # pre_order_setting_number = models.CharField(max_length=20, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    discounted_price = models.FloatField()
    unit_quantity = models.FloatField()
    target_quantity = models.FloatField()
    slug = models.SlugField(max_length=300, unique=True, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    # note = models.CharField(max_length=500, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.product.product_name

    def save(self, *args, **kwargs):
        # if self.end_date < timezone.now():
        #     self.is_approved = False
        self.slug = self.product.slug + "-" + str(self.producer_product.id)
        super(PreOrderSetting, self).save(*args, **kwargs)


class PreOrder(BaseModel):
    """
    This is the model for Pre Order placed by customer
    """
    WEBSITE = 'WB'
    ADMIN_PANEL = 'AD'
    MOBILE_APPLICATION = 'AP'
    PLATFORM = [
        (WEBSITE, 'Website'),
        (ADMIN_PANEL, 'Admin Panel'),
        (MOBILE_APPLICATION, 'Mobile App')
    ]
    ORDERED = 'OD'  # ORDER PLACED FROM CUSTOMER
    ORDER_ACCEPTED = 'OA'  # ORDER ACCEPTED BY ADMIN
    ORDER_CANCELLED = 'CN'  # ORDER IS CANCELED BY CUSTOMER/ ADMIN
    PRE_ORDER_STATUS = [
        (ORDERED, 'Ordered'),
        (ORDER_ACCEPTED, 'Order Accepted'),
        (ORDER_CANCELLED, 'Order Cancelled'),
    ]
    pre_order_setting = models.ForeignKey(PreOrderSetting, models.CASCADE)
    pre_order_number = models.CharField(max_length=10, unique=True)
    customer = models.ForeignKey(UserProfile, models.SET_NULL, null=True)
    delivery_address = models.ForeignKey(Address, models.SET_NULL, null=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    product_quantity = models.FloatField()
    note = models.CharField(max_length=500, null=True, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM, default=WEBSITE)
    pre_order_status = models.CharField(max_length=100, choices=PRE_ORDER_STATUS, default=ORDERED)
    order = models.OneToOneField(Order, models.SET_NULL, null=True, blank=True)
    # is_cancelled = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return '{}'.format(self.id)
