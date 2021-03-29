from utility.notification import send_sms


def send_coupon_sms(coupon, mobile_number):
    if coupon.coupon_code_type == 'RC':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"আরও আকর্ষণীয় কুপন পেতে, রেফারেল কুপন শেয়ার করুন! " \
                   f"নিচের রেফারেল কুপন ব্যবহার করলে, সদাই-তে আপনার বন্ধু বা আত্মীয় পাবে {coupon.discount_percent}% ডিসকাউন্ট! " \
                   f"{coupon.minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {coupon.discount_amount_limit} টাকা!। " \
                   f"আর প্রতিটি সফল রেফারেলে নিজের জন্যও পাবেন নতুন আকর্ষণীয় কুপন।\n" \
                   f"রেফারেল কুপন কোডঃ {coupon.coupon_code}\n" \
                   f"রেফারেল কুপনের মেয়াদঃ {coupon.expiry_date.date()}\n" \
                   f"সফল রেফারেল বাকি আছেঃ {coupon.max_usage_count}\n\n" \
                   f"www.shod.ai"
    elif coupon.coupon_code_type == 'DC':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"অভিনন্দন! আপনার সফল রেফারেলের জন্য, " \
                   f"আপনি পেয়েছেন {coupon.discount_percent}% ডিসকাউন্টের কুপন! " \
                   f"{coupon.minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {coupon.discount_amount_limit} টাকা!। " \
                   f"আপনার পরবর্তী ক্রয়ে আকর্ষণীয় ছাড় পেতে এই কুপনটি [{coupon.coupon_code}] ব্যবহার করুন।\n" \
                   f"কুপনের মেয়াদঃ {coupon.expiry_date.date()}\n\n" \
                   f"www.shod.ai"
    elif coupon.coupon_code_type == 'GC1':
        sms_body = f"প্রিয় গ্রাহক,\n" \
                   f"সদাইতে সাইন আপ করায় আপনার জন্য ফ্রি কুপন! " \
                   f"{coupon.discount_percent}% ডিসকাউন্ট! " \
                   f"{coupon.minimum_purchase_limit}+ টাকার বাজারে, সর্বোচ্চ {coupon.discount_amount_limit} টাকা!।\n" \
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
