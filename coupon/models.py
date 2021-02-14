from django.db import models

# Create your models here.
from simple_history.models import HistoricalRecords

from bases.models import BaseModel
# from order.models import Order, InvoiceInfo
from userProfile.models import UserProfile

DISCOUNT_PERCENT = 'DP'
DISCOUNT_AMOUNT = 'DA'
DISCOUNT_TYPE = [
    (DISCOUNT_PERCENT, 'Discount Percent'),
    (DISCOUNT_AMOUNT, 'Discount Amount'),
]


class CouponCode(BaseModel):
    REFERRAL_CODE = 'RC'
    DISCOUNT_CODE = 'DC'
    PROMOTIONAL_CODE = 'PC'
    COUPON_TYPE = [
        (REFERRAL_CODE, 'Referral Code'),
        (DISCOUNT_CODE, 'Discount Code'),
        (PROMOTIONAL_CODE, 'Promotional Code'),
    ]

    name = models.CharField(max_length=100, default="")
    coupon_code = models.CharField(max_length=10, unique=True, null=False, blank=False)
    discount_percent = models.FloatField(default=0, blank=True, null=True, verbose_name='Discount Percent(%)')
    discount_amount = models.FloatField(default=0, blank=True, null=True, verbose_name='Flat Discount')
    discount_amount_limit = models.IntegerField(default=0, blank=True, null=True, )
    max_usage_count = models.IntegerField(default=0, blank=True, null=True, )
    expiry_date = models.DateTimeField(null=False, blank=False)
    discount_type = models.CharField(max_length=30, choices=DISCOUNT_TYPE, default=DISCOUNT_AMOUNT)
    coupon_code_type = models.CharField(max_length=30, choices=COUPON_TYPE, default=PROMOTIONAL_CODE)
    history = HistoricalRecords()

    def __str__(self):
        return "{}".format(self.id)


class CouponUser(BaseModel):
    created_for = models.ForeignKey(UserProfile, models.SET_NULL, blank=True, null=True, verbose_name="Created For")
    remaining_usage_count = models.IntegerField(default=0, blank=True, null=True, )
    coupon_code = models.ForeignKey(CouponCode, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.id)


class CouponCodeHistory(BaseModel):
    discount_percent = models.FloatField(default=0, blank=True, null=True, verbose_name='Discount Percent(%)')
    discount_amount = models.FloatField(default=0, blank=True, null=True, verbose_name='Flat Discount')
    discount_type = models.CharField(max_length=30, choices=DISCOUNT_TYPE, default=DISCOUNT_AMOUNT)
    coupon_code = models.ForeignKey(CouponCode, on_delete=models.CASCADE)
    coupon_user = models.ForeignKey(CouponUser, models.SET_NULL, blank=True, null=True, verbose_name="Created For")
    order = models.ForeignKey(to='order.Order', on_delete=models.CASCADE)
    invoice_number = models.ForeignKey(to='order.InvoiceInfo', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + " - " + "Coupon: " + str(self.coupon_code)
