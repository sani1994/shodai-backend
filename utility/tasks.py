from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.template.loader import get_template
from django.utils import timezone

from order.models import Order
from user.models import UserProfile


def send_daily_summary_email():
    today = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    this_month = timezone.localtime().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    order_placed_daily = Order.objects.filter(placed_on__gte=today).exclude(order_status='CN')
    order_placed_monthly = Order.objects.filter(placed_on__gte=this_month).exclude(order_status='CN')
    total_order_placed = Order.objects.all().exclude(order_status='CN')

    order_amount_daily = order_placed_daily.aggregate(Sum('order_total_price')).get('order_total_price__sum')
    order_amount_monthly = order_placed_monthly.aggregate(Sum('order_total_price')).get('order_total_price__sum')
    total_order_amount = total_order_placed.aggregate(Sum('order_total_price')).get('order_total_price__sum')

    user_daily = set([order.user for order in order_placed_daily])
    user_monthly = set([order.user for order in order_placed_monthly])
    total_user = UserProfile.objects.filter(user_type='CM', is_active=True, is_approved=True)
    new_customer_daily = new_customer_monthly = total_new_customer = 0
    repeated_customer_daily = repeated_customer_monthly = total_repeated_customer = 0
    for user in user_daily:
        user_first_order = Order.objects.filter(user=user).exclude(order_status='CN').order_by('created_on').first()
        if user_first_order.created_on >= today:
            new_customer_daily += 1
        else:
            repeated_customer_daily += 1
    for user in user_monthly:
        user_first_order = Order.objects.filter(user=user).exclude(order_status='CN').order_by('created_on').first()
        if user_first_order.created_on >= this_month:
            new_customer_monthly += 1
        else:
            repeated_customer_monthly += 1
    for user in total_user:
        user_order = Order.objects.filter(user=user).exclude(order_status='CN').count()
        if user_order == 1:
            total_new_customer += 1
        elif user_order > 1:
            total_repeated_customer += 1

    content = {"date": today.date(),

               "order_placed_daily": order_placed_daily.count(),
               "order_placed_from_web_daily": Order.objects.filter(placed_on__gte=today, platform='WB').exclude(order_status='CN').count(),
               "order_placed_from_admin_daily": Order.objects.filter(placed_on__gte=today, platform='AD').exclude(order_status='CN').count(),
               "order_delivered_daily": Order.objects.filter(modified_on__gte=today, order_status='COM').count(),
               "order_amount_daily": int(order_amount_daily) if order_amount_daily else 0,

               "order_placed_monthly": order_placed_monthly.count(),
               "order_placed_from_web_monthly": Order.objects.filter(placed_on__gte=this_month, platform='WB').exclude(order_status='CN').count(),
               "order_placed_from_admin_monthly": Order.objects.filter(placed_on__gte=this_month, platform='AD').exclude(order_status='CN').count(),
               "order_delivered_monthly": Order.objects.filter(modified_on__gte=this_month, order_status='COM').count(),
               "order_amount_monthly": int(order_amount_monthly) if order_amount_monthly else 0,

               "total_order_placed": total_order_placed.count(),
               "total_order_placed_from_web": Order.objects.filter(platform='WB').exclude(order_status='CN').count(),
               "total_order_placed_from_admin": Order.objects.filter(platform='AD').exclude(order_status='CN').count(),
               "total_order_delivered": Order.objects.filter(order_status='COM').count(),
               "total_order_amount": int(total_order_amount) if total_order_amount else 0,

               "new_customer_daily": new_customer_daily,
               "new_customer_monthly": new_customer_monthly,
               "total_new_customer": total_new_customer,

               "repeated_customer_daily": repeated_customer_daily,
               "repeated_customer_monthly": repeated_customer_monthly,
               "total_repeated_customer": total_repeated_customer

               # "registered_customer_daily": UserProfile.objects.filter(created_on__gte=today).count(),
               # "registered_customer_monthly": UserProfile.objects.filter(created_on__gte=this_month).count(),
               # "total_registered_customer": total_user.count()
               }

    subject = f"Shodai Daily Summary - {today.date()}"
    from_email = 'shod.ai <noreply@shod.ai>'
    to_emails = config("DAILY_SUMMARY_STAFF_EMAILS").replace(" ", "").split(',')
    html_summary = get_template('email/daily_summary.html')
    html_content = html_summary.render(content)
    msg = EmailMultiAlternatives(subject, 'shodai', from_email, to_emails)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return content
