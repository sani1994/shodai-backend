from django.utils import timezone
from order.models import Order
from user.models import UserProfile


def send_summary_email():
    today = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    this_month = timezone.localtime().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    order_placed_daily = Order.objects.filter(placed_on__gte=today).exclude(order_status='CN')
    order_placed_monthly = Order.objects.filter(placed_on__gte=this_month).exclude(order_status='CN')

    user_daily = set([order.user for order in order_placed_daily])
    user_monthly = set([order.user for order in order_placed_monthly])
    total_user = UserProfile.objects.filter(user_type='CM', is_active=True, is_approved=True)
    repeated_customer_daily = repeated_customer_monthly = total_repeated_customer = 0
    for user in user_daily:
        user_order = Order.objects.filter(placed_on__lt=today, user=user).exclude(order_status='CN').count()
        if user_order:
            repeated_customer_daily += 1
    for user in user_monthly:
        user_order = Order.objects.filter(placed_on__lt=this_month, user=user).exclude(order_status='CN').count()
        if user_order:
            repeated_customer_monthly += 1
    for user in total_user:
        user_order = Order.objects.filter(user=user).exclude(order_status='CN').count()
        if user_order > 1:
            total_repeated_customer += 1

    payload = {"customer_daily": UserProfile.objects.filter(created_on__gte=today).count(),
               "customer_monthly": UserProfile.objects.filter(created_on__gte=this_month).count(),
               "total_customer": total_user.count(),

               "order_placed_daily": order_placed_daily.count(),
               "order_placed_from_web_daily": Order.objects.filter(placed_on__gte=today, platform='WB').exclude(order_status='CN').count(),
               "order_placed_from_admin_daily": Order.objects.filter(placed_on__gte=today, platform='AD').exclude(order_status='CN').count(),
               "order_delivered_daily": Order.objects.filter(placed_on__gte=today, order_status='COM').count(),

               "order_placed_monthly": order_placed_monthly.count(),
               "order_placed_from_web_monthly": Order.objects.filter(placed_on__gte=this_month, platform='WB').exclude(order_status='CN').count(),
               "order_placed_from_admin_monthly": Order.objects.filter(placed_on__gte=this_month, platform='AD').exclude(order_status='CN').count(),
               "order_delivered_monthly": Order.objects.filter(placed_on__gte=this_month, order_status='COM').count(),

               "total_order_placed": Order.objects.all().exclude(order_status='CN').count(),
               "total_order_placed_from_web": Order.objects.filter(platform='WB').exclude(order_status='CN').count(),
               "total_order_placed_from_admin": Order.objects.filter(platform='AD').exclude(order_status='CN').count(),
               "total_order_delivered": Order.objects.filter(order_status='COM').count(),

               "repeated_customer_daily": repeated_customer_daily,
               "repeated_customer_monthly": repeated_customer_monthly,
               "total_repeated_customer": total_repeated_customer}
