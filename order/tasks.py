from django.utils import timezone

from order.models import Order
from userProfile.models import UserProfile


def send_summary_email():
    today = timezone.now().date()
    orders_daily = Order.objects.filter(placed_on__contains=today, order_status='COM')
    users_daily = [order.user for order in orders_daily]
    repeat_customer_daily = repeat_customer_monthly = 0
    for user in users_daily:
        completed_order = Order.objects.filter(placed_on__day__lt=today.day, user=user, order_status='COM')
        if completed_order:
            repeat_customer_daily += 1
    orders_monthly = Order.objects.filter(placed_on__month=today.month, order_status='COM')
    users_monthly = [order.user for order in orders_monthly]
    for user in users_monthly:
        completed_order = Order.objects.filter(placed_on__month__lt=today.month, user=user, order_status='COM')
        if completed_order:
            repeat_customer_monthly += 1

    payload = {"new_client_daily": UserProfile.objects.filter(created_on__contains=today).count(),
               "new_client_monthly": UserProfile.objects.filter(created_on__month=today.month).count(),
               "total_client": UserProfile.objects.all().count(),
               "order_daily": Order.objects.filter(placed_on__contains=today).count().exclude(order_status='CN'),
               "order_placed_from_web_daily": Order.objects.filter(placed_on__contains=today, platform='WB').count().exclude(order_status='CN'),
               "order_placed_from_admin_daily": Order.objects.filter(placed_on__contains=today, platform='AD').count().exclude(order_status='CN'),
               "order_delivered_daily": orders_daily.count(),
               "order_monthly": Order.objects.filter(placed_on__month=today.month).count().exclude(order_status='CN'),
               "order_placed_from_web_monthly": Order.objects.filter(placed_on__month=today.month, platform='WB').count().exclude(
                   order_status='CN'),
               "order_placed_from_admin_monthly": Order.objects.filter(placed_on__month=today.month, platform='AD').count().exclude(
                   order_status='CN'),
               "order_delivered_monthly": orders_monthly.count(),
               "total_order": Order.objects.all().count().exclude(order_status='CN'),
               "total_order_placed_from_web": Order.objects.filter(platform='WB').count().exclude(order_status='CN'),
               "total_order_placed_from_admin": Order.objects.filter(platform='AD').count().exclude(order_status='CN'),
               "total_order_delivered": Order.objects.filter(order_status='COM').count(),
               "repeat_customer_daily": repeat_customer_daily,
               "repeat_customer_monthly": repeat_customer_monthly}
