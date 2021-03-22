import uuid
from datetime import timedelta

from django.contrib.gis.geos import GEOSGeometry
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django_q.tasks import async_task

from coupon.models import CouponCode, CouponUser
from order.models import Order, InvoiceInfo, DiscountInfo


@receiver(pre_save, sender=Order)
def order_data_preprocessing(sender, instance, **kwargs):
    if not instance.order_number:
        last_order = Order.objects.last()
        while "-" in last_order.order_number:
            last_order = Order.objects.get(id=last_order.id - 1)
        instance.order_number = str(int(last_order.order_number) + 1)
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
                new_coupon = CouponCode.objects.create(coupon_code=str(uuid.uuid4())[:6].upper(),
                                                       name="Discount Code",
                                                       discount_percent=5,
                                                       max_usage_count=1,
                                                       minimum_purchase_limit=0,
                                                       discount_amount_limit=200,
                                                       expiry_date=timezone.now() + timedelta(days=30),
                                                       discount_type='DP',
                                                       coupon_code_type='DC',
                                                       created_by=instance.user,
                                                       created_on=timezone.now())
                CouponUser.objects.create(coupon_code=new_coupon,
                                          created_for=coupon.created_by,
                                          remaining_usage_count=1,
                                          created_by=instance.user,
                                          created_on=timezone.now())
    instance.currency = 'BDT'
    instance.order_geopoint = GEOSGeometry('POINT(%f %f)' % (instance.long, instance.lat))
