from django.db import models

# Create your models here.
from simple_history.models import HistoricalRecords

from base.models import BaseModel
from user.models import UserProfile

DISCOUNT_PERCENT = 'DP'
DISCOUNT_AMOUNT = 'DA'
DISCOUNT_TYPE = [
    (DISCOUNT_PERCENT, 'Discount Percent'),
    (DISCOUNT_AMOUNT, 'Discount Amount'),
]


class CouponCode(BaseModel):
    REFERRAL_COUPON = 'RC'
    DISCOUNT_COUPON = 'DC'
    PROMOTIONAL_COUPON = 'PC'
    GIFT_COUPON_1 = 'GC1'
    GIFT_COUPON_2 = 'GC2'
    COUPON_TYPE = [
        (REFERRAL_COUPON, 'Referral Coupon'),
        (DISCOUNT_COUPON, 'Discount Coupon'),
        (PROMOTIONAL_COUPON, 'Promotional Coupon'),
        (GIFT_COUPON_1, 'Sign Up Coupon'),
        (GIFT_COUPON_2, 'Purchase Coupon'),
    ]

    name = models.CharField(max_length=100, default="")
    coupon_code = models.CharField(max_length=10, unique=True, null=False, blank=False)
    discount_percent = models.FloatField(default=0, verbose_name='Discount Percent(%)')
    discount_amount = models.FloatField(default=0, verbose_name='Flat Discount Amount')
    discount_amount_limit = models.IntegerField(default=0, verbose_name='Maximum Discount Amount')
    minimum_purchase_limit = models.IntegerField(default=0, verbose_name="Minimum Purchase Amount")
    max_usage_count = models.IntegerField(default=0)
    expiry_date = models.DateTimeField(null=False, blank=False)
    discount_type = models.CharField(max_length=30, choices=DISCOUNT_TYPE, default=DISCOUNT_AMOUNT)
    coupon_code_type = models.CharField(max_length=30, choices=COUPON_TYPE, default=PROMOTIONAL_COUPON)
    history = HistoricalRecords()

    def __str__(self):
        return "{}".format(self.id)


class CouponUser(BaseModel):
    created_for = models.ForeignKey(UserProfile, models.SET_NULL, blank=True, null=True)
    remaining_usage_count = models.IntegerField(default=0)
    coupon_code = models.ForeignKey(CouponCode, models.CASCADE, related_name='discount_code')

    def __str__(self):
        return str(self.created_for)


class CouponUsageHistory(BaseModel):
    discount_percent = models.FloatField(default=0, verbose_name='Discount Percent(%)')
    discount_amount = models.FloatField(default=0, verbose_name='Discount Amount')
    discount_type = models.CharField(max_length=30, choices=DISCOUNT_TYPE, default=DISCOUNT_AMOUNT)
    coupon_code = models.CharField(max_length=10, null=False, blank=False)
    coupon_user = models.ForeignKey(CouponUser, models.SET_NULL, null=True, verbose_name="Reference")
    invoice_number = models.ForeignKey(to='order.InvoiceInfo', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.id) + " - " + "Coupon: " + str(self.coupon_code)


class CouponSettings(BaseModel):
    REFERRAL_COUPON = 'RC'
    DISCOUNT_COUPON = 'DC'
    GIFT_COUPON_1 = 'GC1'
    GIFT_COUPON_2 = 'GC2'
    COUPON_TYPE = [
        (REFERRAL_COUPON, 'Referral Coupon'),
        (DISCOUNT_COUPON, 'Discount Coupon'),
        (GIFT_COUPON_1, 'Sign Up Coupon'),
        (GIFT_COUPON_2, 'Purchase Coupon'),
    ]
    coupon_type = models.CharField(max_length=30, choices=COUPON_TYPE, default=DISCOUNT_COUPON)
    discount_type = models.CharField(max_length=30, choices=DISCOUNT_TYPE, default=DISCOUNT_PERCENT)
    discount_percent = models.FloatField(default=0, verbose_name='Discount Percent(%)')
    discount_amount = models.FloatField(default=0, verbose_name='Flat Discount Amount')
    discount_amount_limit = models.IntegerField(default=0, verbose_name='Maximum Discount Amount')
    minimum_purchase_limit = models.IntegerField(default=0, verbose_name="Minimum Purchase Amount")
    max_usage_count = models.IntegerField(default=1)
    validity_period = models.IntegerField(default=0, verbose_name="Validity Period (Days)")
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.coupon_type
