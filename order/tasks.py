from django.utils import timezone
from order.models import Order
from user.models import UserProfile


def send_summary_email():
    today = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    this_month = timezone.localtime().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    orders_daily = Order.objects.filter(placed_on__gte=today, order_status='COM')
    users_daily = set([order.user for order in orders_daily])
    repeat_customer_daily = repeat_customer_monthly = total_repeat_customer = 0
    for user in users_daily:
        completed_order = Order.objects.filter(placed_on__lt=today, user=user, order_status='COM').count()
        if completed_order:
            repeat_customer_daily += 1
    orders_monthly = Order.objects.filter(placed_on__gte=this_month, order_status='COM')
    users_monthly = set([order.user for order in orders_monthly])
    for user in users_monthly:
        completed_order = Order.objects.filter(placed_on__lt=this_month, user=user, order_status='COM').count()
        if completed_order:
            repeat_customer_monthly += 1
    all_user = UserProfile.objects.all()
    for user in all_user:
        completed_order = Order.objects.filter(user=user, order_status='COM').count()
        if completed_order > 1:
            total_repeat_customer += 1

    payload = {"new_client_daily": UserProfile.objects.filter(created_on__gte=today).count(),
               "new_client_monthly": UserProfile.objects.filter(created_on__gte=this_month).count(),
               "total_client": all_user.count(),
               "order_placed_daily": Order.objects.filter(placed_on__gte=today).exclude(order_status='CN').count(),
               "order_placed_from_web_daily": Order.objects.filter(placed_on__gte=today, platform='WB').exclude(order_status='CN').count(),
               "order_placed_from_admin_daily": Order.objects.filter(placed_on__gte=today, platform='AD').exclude(order_status='CN').count(),
               "order_delivered_daily": orders_daily.count(),
               "order__placed_monthly": Order.objects.filter(placed_on__gte=this_month).exclude(order_status='CN').count(),
               "order_placed_from_web_monthly": Order.objects.filter(placed_on__gte=this_month, platform='WB').exclude(order_status='CN').count(),
               "order_placed_from_admin_monthly": Order.objects.filter(placed_on__gte=this_month, platform='AD').exclude(order_status='CN').count(),
               "order_delivered_monthly": orders_monthly.count(),
               "total_order_placed": Order.objects.all().exclude(order_status='CN').count(),
               "total_order_placed_from_web": Order.objects.filter(platform='WB').exclude(order_status='CN').count(),
               "total_order_placed_from_admin": Order.objects.filter(platform='AD').exclude(order_status='CN').count(),
               "total_order_delivered": Order.objects.filter(order_status='COM').count(),
               "repeat_customer_daily": repeat_customer_daily,
               "repeat_customer_monthly": repeat_customer_monthly,
               "total_repeat_customer": total_repeat_customer}
