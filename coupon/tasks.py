from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from coupon.models import CouponSettings
from utility.notification import send_sms


def send_coupon_sms(coupon, mobile_number):
    if coupon.coupon_code_type == 'RC':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"আরও আকর্ষণীয় কুপন পেতে, রেফারেল কুপন শেয়ার করুন! " \
                   f"এই রেফারেল কুপন [{coupon.coupon_code}] ব্যবহার করলে, সদাই-তে আপনার বন্ধু " \
                   f"বা আত্মীয় পাবে {coupon.discount_percent}% ডিসকাউন্ট! " \
                   f"{coupon.minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {coupon.discount_amount_limit} টাকা! " \
                   f"আর প্রতিটি সফল রেফারেলে নিজের জন্যও পাবেন নতুন আকর্ষণীয় কুপন।\n" \
                   f"কুপনের মেয়াদঃ {coupon.expiry_date.date()}\n" \
                   f"রেফারেল বাকি আছেঃ {coupon.max_usage_count}\n\n" \
                   f"www.shod.ai"
    elif coupon.coupon_code_type == 'DC':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"অভিনন্দন! আপনার সফল রেফারেলের জন্য, " \
                   f"আপনি পেয়েছেন {coupon.discount_percent}% ডিসকাউন্টের কুপন! " \
                   f"{coupon.minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {coupon.discount_amount_limit} টাকা! " \
                   f"আপনার পরবর্তী ক্রয়ে আকর্ষণীয় ছাড় পেতে এই কুপনটি [{coupon.coupon_code}] ব্যবহার করুন।\n" \
                   f"কুপনের মেয়াদঃ {coupon.expiry_date.date()}\n\n" \
                   f"www.shod.ai"
    elif coupon.coupon_code_type == 'GC1':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"সদাইতে সাইন আপ করায় আপনার জন্য ফ্রি কুপন! " \
                   f"{coupon.discount_percent}% ডিসকাউন্ট! " \
                   f"{coupon.minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {coupon.discount_amount_limit} টাকা!\n" \
                   f"কুপন কোডঃ {coupon.coupon_code}\n" \
                   f"কুপনের মেয়াদঃ {coupon.expiry_date.date()}\n\n" \
                   f"www.shod.ai"
    elif coupon.coupon_code_type == 'GC2':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"অভিনন্দন! আপনার সফল ক্রয়ের জন্য, " \
                   f"আপনি পেয়েছেন {coupon.discount_percent}% ডিসকাউন্টের কুপন! " \
                   f"{coupon.minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {coupon.discount_amount_limit} টাকা!\n" \
                   f"কুপন কোডঃ {coupon.coupon_code}\n" \
                   f"কুপনের মেয়াদঃ {coupon.expiry_date.date()}\n\n" \
                   f"www.shod.ai"

    status = send_sms(mobile_number, sms_body)
    return f"{status} {mobile_number} {coupon.coupon_code_type}"


def send_coupon_email(coupon, user):
    if user.first_name and user.last_name:
        customer_name = user.first_name + " " + user.last_name
    elif user.first_name:
        customer_name = user.first_name
    else:
        customer_name = "Customer"

    gift_coupon_purchase_limit = CouponSettings.objects.get(coupon_type='GC2').minimum_purchase_limit

    content = {'customer_name': customer_name,
               'coupon_type': coupon.coupon_code_type,
               'coupon_code': coupon.coupon_code,
               'discount_percent': int(coupon.discount_percent),
               'gift_coupon_purchase_limit': gift_coupon_purchase_limit,
               'api_domain': settings.API_DOMAIN}

    if coupon.coupon_code_type == 'RC':
        subject = 'You have referral Coupon to share from shod.ai'
    else:
        subject = 'You got a new Coupon from shod.ai'
    from_email, to = 'noreply@shod.ai', user.email
    html_customer = get_template('coupon_email.html')
    html_content = html_customer.render(content)
    msg = EmailMultiAlternatives(subject, 'shodai', from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return f"{coupon.coupon_code_type} sent to {user.email}"
