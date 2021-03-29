import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django_q.tasks import async_task
from coupon.models import CouponCode, CouponUser, CouponSettings
from order.models import Order, InvoiceInfo, DiscountInfo


@receiver(pre_save, sender=Order)
def order_data_preprocessing(sender, instance, **kwargs):
    if not instance.order_number:
        last_order = Order.objects.last()
        while "-" in last_order.order_number:
            last_order = Order.objects.get(id=last_order.id - 1)
        instance.order_number = str(int(last_order.order_number) + 1)

    instance.currency = 'BDT'
    instance.order_geopoint = GEOSGeometry('POINT(%f %f)' % (instance.long, instance.lat))

    if instance.order_status == "COM":
        invoice = InvoiceInfo.objects.get(invoice_number=instance.invoice_number)
        if invoice.payment_method == "CASH_ON_DELIVERY":
            if not invoice.paid_status:
                invoice.paid_status = True
                invoice.paid_on = timezone.now()
                invoice.save()
        elif invoice.payment_method == "SSLCOMMERZ":
            if not invoice.paid_status:
                invoice.payment_method = "CASH_ON_DELIVERY"
                invoice.paid_status = True
                invoice.paid_on = timezone.now()
                invoice.save()

        discount = DiscountInfo.objects.filter(discount_type='CP', invoice=invoice)
        if discount and discount[0].coupon:
            coupon = discount[0].coupon
            if coupon.coupon_code_type == 'RC':
                discount_settings = CouponSettings.objects.get(coupon_type='DC')
                new_coupon = CouponCode.objects.create(coupon_code=str(uuid.uuid4())[:6].upper(),
                                                       name="Discount Coupon",
                                                       discount_percent=discount_settings.discount_percent,
                                                       discount_amount=discount_settings.discount_amount,
                                                       max_usage_count=discount_settings.max_usage_count,
                                                       minimum_purchase_limit=discount_settings.minimum_purchase_limit,
                                                       discount_amount_limit=discount_settings.discount_amount_limit,
                                                       expiry_date=timezone.now() + timedelta(
                                                           days=discount_settings.validity_period),
                                                       discount_type=discount_settings.discount_type,
                                                       coupon_code_type='DC',
                                                       created_by=instance.user,
                                                       created_on=timezone.now())
                CouponUser.objects.create(coupon_code=new_coupon,
                                          created_for=coupon.created_by,
                                          remaining_usage_count=1,
                                          created_by=instance.user,
                                          created_on=timezone.now())
                if not settings.DEBUG:
                    async_task('coupon.tasks.send_coupon_sms',
                               new_coupon,
                               coupon.created_by.mobile_number)

        if instance.platform == 'WB':
            gift_coupon_settings = CouponSettings.objects.get(coupon_type='GC2')
            if gift_coupon_settings.is_active:
                gift_coupon = CouponCode.objects.create(coupon_code=str(uuid.uuid4())[:6].upper(),
                                                        name="Purchase Coupon",
                                                        discount_percent=gift_coupon_settings.discount_percent,
                                                        discount_amount=gift_coupon_settings.discount_amount,
                                                        max_usage_count=gift_coupon_settings.max_usage_count,
                                                        minimum_purchase_limit=gift_coupon_settings.minimum_purchase_limit,
                                                        discount_amount_limit=gift_coupon_settings.discount_amount_limit,
                                                        expiry_date=timezone.now() + timedelta(
                                                            days=gift_coupon_settings.validity_period),
                                                        discount_type=gift_coupon_settings.discount_type,
                                                        coupon_code_type='GC2',
                                                        created_by=instance.user,
                                                        created_on=timezone.now())
                CouponUser.objects.create(coupon_code=gift_coupon,
                                          created_for=instance.user,
                                          remaining_usage_count=1,
                                          created_by=instance.user,
                                          created_on=timezone.now())
                if not settings.DEBUG:
                    async_task('coupon.tasks.send_coupon_sms',
                               gift_coupon,
                               instance.user.mobile_number)
