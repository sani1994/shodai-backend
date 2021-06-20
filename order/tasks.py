from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone

from order.models import DeliveryCharge, OrderProduct, InvoiceInfo, DiscountInfo, TimeSlot
from shodai_admin.serializers import platform_all


def send_order_email(order, is_pre_order=False):
    user = order.user
    if user.email:
        invoice = InvoiceInfo.objects.filter(order_number=order).order_by('-created_on').first()
        product_list = OrderProduct.objects.filter(order=order)
        matrix = []
        is_product_discount = False
        product_total_price = 0
        for p in product_list:
            if p.order_product_price != p.product_price:
                is_product_discount = True
                total_by_offer = float(p.order_product_price) * p.order_product_qty
                product_total_price += total_by_offer
                col = [p.product.product_name, p.product.product_unit, p.product_price,
                       p.order_product_price, int(p.order_product_qty), total_by_offer]
            else:
                total = float(p.product_price) * p.order_product_qty
                product_total_price += total
                col = [p.product.product_name, p.product.product_unit, p.product_price,
                       "--", int(p.order_product_qty), total]
            matrix.append(col)

        is_coupon_discount = DiscountInfo.objects.filter(discount_type='CP', invoice=invoice).first()
        coupon_discount = is_coupon_discount.discount_amount if is_coupon_discount else 0
        delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
        client_name = invoice.billing_person_name
        time_slot = TimeSlot.objects.filter(time=timezone.localtime(order.delivery_date_time).time()).first()
        time = " ( " + time_slot.slot + " )" if time_slot else ""
        if order.address and order.address.road:
            address = order.address.road + " " + order.address.city
        else:
            address = invoice.delivery_address

        content = {'user_name': client_name,
                   'order_number': order.order_number,
                   'shipping_address': address,
                   'mobile_no': order.contact_number,
                   'order_date': order.created_on.date(),
                   'delivery_date_time': str(
                       order.delivery_date_time.date()) + time,
                   'sub_total': product_total_price,
                   'vat': order.total_vat,
                   'delivery_charge': delivery_charge,
                   'total': order.order_total_price,
                   'order_details': matrix,
                   'is_product_discount': is_product_discount,
                   'coupon_discount': coupon_discount,
                   'delivery_charge_discount': 0,
                   'saved_amount': invoice.discount_amount,
                   'note': order.note if order.note else None,
                   'colspan_value': "4" if is_product_discount else "3",
                   'is_pre_order': is_pre_order}

        subject = 'Your shodai order (#' + str(order.order_number) + ') summary'
        from_email, to = 'noreply@shod.ai', user.email
        html_customer = get_template('email/order_notification_customer.html')
        html_content = html_customer.render(content)
        msg = EmailMultiAlternatives(subject, 'shodai', from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        if not is_pre_order:
            content = {'user_name': client_name,
                       'user_mobile': user.mobile_number,
                       'order_number': order.order_number,
                       'platform': platform_all[order.platform],
                       'shipping_address': address,
                       'mobile_no': order.contact_number,
                       'order_date': order.created_on.date(),
                       'delivery_date_time': str(
                           order.delivery_date_time.date()) + time,
                       'invoice_number': invoice.invoice_number,
                       'payment_method': "Cash on Delivery" if invoice.payment_method == "CASH_ON_DELIVERY" else "Online Payment",
                       'sub_total': product_total_price,
                       'vat': order.total_vat,
                       'delivery_charge': delivery_charge,
                       'total': order.order_total_price,
                       'order_details': matrix,
                       'is_product_discount': is_product_discount,
                       'coupon_discount': coupon_discount,
                       'delivery_charge_discount': 0,
                       'saved_amount': invoice.discount_amount,
                       'note': order.note if order.note else None,
                       'colspan_value': "4" if is_product_discount else "3"}

            admin_subject = 'Order (#' + str(order.order_number) + ') has been placed'
            admin_email = config("ORDER_NOTIFICATION_STAFF_EMAILS").replace(" ", "").split(',')
            html_admin = get_template('email/order_notification_staff.html')
            html_content = html_admin.render(content)
            msg_to_admin = EmailMultiAlternatives(admin_subject, 'shodai', from_email, admin_email)
            msg_to_admin.attach_alternative(html_content, "text/html")
            msg_to_admin.send()

        return f"{order.order_number} sent to {user.email}"
    else:
        return f"email not found"


def send_pre_order_email(pre_order, is_cancelled=False):
    user = pre_order.customer
    if user.email:
        if user.first_name and user.last_name:
            customer_name = user.first_name + " " + user.last_name
        elif user.first_name:
            customer_name = user.first_name
        else:
            customer_name = "Customer"

        product_price = pre_order.pre_order_setting.discounted_price
        column = [pre_order.pre_order_setting.product.product_name,
                  pre_order.pre_order_setting.product.product_unit.product_unit,
                  pre_order.pre_order_setting.product.product_price,
                  product_price, int(pre_order.product_quantity),
                  product_price * pre_order.product_quantity]
        product_price_with_vat = round(product_price + (product_price *
                                                        pre_order.pre_order_setting.product.product_meta.vat_amount) / 100)
        total_vat = float(product_price_with_vat - product_price) * pre_order.product_quantity
        delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
        sub_total = product_price * pre_order.product_quantity
        sub_total_without_offer = float(pre_order.pre_order_setting.product.product_price) * pre_order.product_quantity
        html_pre_order = get_template('email/pre_order_notification.html')

        if not is_cancelled:
            user_email_content = {'is_customer': True,
                                  'user_name': customer_name,
                                  'order_number': pre_order.pre_order_number,
                                  'shipping_address': pre_order.delivery_address.road + " " + pre_order.delivery_address.city,
                                  'mobile_no': pre_order.contact_number,
                                  'order_date': pre_order.created_on.date(),
                                  'delivery_date_time': pre_order.pre_order_setting.delivery_date.date(),
                                  'sub_total': sub_total,
                                  'vat': total_vat,
                                  'delivery_charge': delivery_charge,
                                  'total': sub_total + total_vat + delivery_charge,
                                  'details': column,
                                  'saved_amount': sub_total_without_offer - sub_total,
                                  'note': pre_order.note if pre_order.note else None}

            subject = 'Your shodai pre-order (#' + str(pre_order.pre_order_number) + ') details'
            from_email, to = 'noreply@shod.ai', user.email
            html_customer_content = html_pre_order.render(user_email_content)
            msg = EmailMultiAlternatives(subject, 'shodai', from_email, [to])
            msg.attach_alternative(html_customer_content, "text/html")
            msg.send()

            admin_email_content = {'user_name': customer_name,
                                   'user_mobile': user.mobile_number,
                                   'platform': platform_all[pre_order.platform],
                                   'order_number': pre_order.pre_order_number,
                                   'shipping_address': pre_order.delivery_address.road + " " + pre_order.delivery_address.city,
                                   'mobile_no': pre_order.contact_number,
                                   'order_date': pre_order.created_on.date(),
                                   'delivery_date_time': pre_order.pre_order_setting.delivery_date.date(),
                                   'sub_total': sub_total,
                                   'vat': total_vat,
                                   'delivery_charge': delivery_charge,
                                   'total': sub_total + total_vat + delivery_charge,
                                   'details': column,
                                   'saved_amount': sub_total_without_offer - sub_total,
                                   'note': pre_order.note if pre_order.note else None}

            admin_subject = 'Pre-order (#' + str(pre_order.pre_order_number) + ') has been placed'
            admin_email = config("ORDER_NOTIFICATION_STAFF_EMAILS").replace(" ", "").split(',')
            html_admin_content = html_pre_order.render(admin_email_content)
            msg_to_admin = EmailMultiAlternatives(admin_subject, 'shodai', from_email, admin_email)
            msg_to_admin.attach_alternative(html_admin_content, "text/html")
            msg_to_admin.send()
        else:
            user_email_content = {'user_name': customer_name,
                                  'order_number': pre_order.pre_order_number,
                                  'sub_total': sub_total,
                                  'vat': total_vat,
                                  'delivery_charge': delivery_charge,
                                  'total': sub_total + total_vat + delivery_charge,
                                  'details': column,
                                  'is_cancelled': True,
                                  'is_customer': True}
            subject = 'Your shodai pre-order (#' + str(pre_order.pre_order_number) + ') has been cancelled'
            from_email, to = 'noreply@shod.ai', user.email
            html_customer_content = html_pre_order.render(user_email_content)
            msg = EmailMultiAlternatives(subject, 'shodai', from_email, [to])
            msg.attach_alternative(html_customer_content, "text/html")
            msg.send()

        return f"{pre_order.pre_order_number} sent to {user.email}"
    else:
        return f"email not found"
