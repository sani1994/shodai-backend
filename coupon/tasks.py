from utility.notification import send_sms


def send_coupon_sms(sms_type, coupon_code, discount_percent, mobile_number):
    if sms_type == 'RC':
        sms_body = f"Dear Customer,\n" \
                   f"Don't forget to share this code [{coupon_code}] with your " \
                   f"friends and family to avail them {discount_percent}% discount " \
                   f"on their next purchase and " \
                   f"receive exciting discount after each successful referral.\n\n" \
                   f"www.shod.ai"
    elif sms_type == 'DC':
        sms_body = f"Dear Customer,\n" \
                   f"Congratulations! You have received {discount_percent}% discount " \
                   f"based on your successful referral. " \
                   f"Use this code [{coupon_code}] to " \
                   f"avail exciting discount on your next purchase.\n\n" \
                   f"www.shod.ai"
    elif sms_type == 'GC1':
        sms_body = f"Dear Customer,\n" \
                   f"Congratulations on your new Shodai account! " \
                   f"Use this code [{coupon_code}] " \
                   f"to avail a {discount_percent}% discount on your first order.\n\n" \
                   f"www.shod.ai"
    elif sms_type == 'GC2':
        sms_body = f"Dear Customer,\n" \
                   f"Congratulations! You have received {discount_percent}% discount " \
                   f"based on your successful purchase. " \
                   f"Use code [{coupon_code}] to " \
                   f"avail this discount on your next order.\n\n" \
                   f"www.shod.ai"

    status = send_sms(mobile_number, sms_body)
    return f"{status} {mobile_number} {sms_type}"
