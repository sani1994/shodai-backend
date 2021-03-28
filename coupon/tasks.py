from utility.notification import send_sms


def send_coupon_sms(sms_type, coupon_code, discount_percent, mobile_number, minimum_purchase_limit,
                    discount_amount_limit, expiry_date, max_usage_count):
    if sms_type == 'RC':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"আরও আকর্ষণী কুপন পেতে, রেফারেল কুপন শেয়ার করুন! " \
                   f"নিচের রেফারেল কুপন ব্যবহার করলে, সদাই-তে আপনার বন্ধু বা আত্মীয় পাবে {discount_percent}% ডিসকাউন্ট! " \
                   f"{minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {discount_amount_limit} টাকা!। \n" \
                   f"আর প্রতিটি সফল রেফারেলে নিজের জন্যও পাবেন নতুন আকর্ষণীয় কুপন। \n" \
                   f"রেফারেল কুপন কোডঃ [{coupon_code}]\n " \
                   f"রেফারেল কুপনের মেয়াদঃ {expiry_date}\n" \
                   f"সফল রেফারেল বাকি আছেঃ {max_usage_count}\n\n" \
                   f"www.shod.ai"
    elif sms_type == 'DC':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"অভিনন্দন! আপনার সফল রেফারেলের জন্যও," \
                   f"আপনি পেয়েছেন {discount_percent}% ডিসকাউন্ট! " \
                   f"{minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {discount_amount_limit} টাকা!। \n" \
                   f"আপনার পরবর্তী ক্রয়ে আকর্ষণীয় ছাড় পেতে এই কোডটি [{coupon_code}] ব্যবহার করুন। \n" \
                   f"কুপনের মেয়াদঃ {expiry_date}\n\n" \
                   f"www.shod.ai"
    elif sms_type == 'GC1':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"সদাইতে সাইন আপ করায় আপনার জন্য ফ্রি কুপন! " \
                   f"{discount_percent}% ডিসকাউন্ট! " \
                   f"{minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {discount_amount_limit} টাকা!। \n" \
                   f"কুপন কোডঃ [{coupon_code}]\n " \
                   f"কুপনের মেয়াদঃ {expiry_date}\n\n" \
                   f"www.shod.ai"
    elif sms_type == 'GC2':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"অভিনন্দন! আপনার সফল ক্রয়ের জন্যও," \
                   f"আপনি পেয়েছেন {discount_percent}% ডিসকাউন্ট! " \
                   f"{minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {discount_amount_limit} টাকা! \n" \
                   f"কুপন কোডঃ [{coupon_code}]\n " \
                   f"কুপনের মেয়াদঃ {expiry_date}\n\n" \
                   f"www.shod.ai"

    status = send_sms(mobile_number, sms_body)
    return f"{status} {mobile_number} {sms_type}"
