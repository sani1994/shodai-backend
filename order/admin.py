from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from order.models import Order, Vat, OrderProduct, DeliveryCharge, PaymentInfo, TimeSlot


# Register your models here.

class TimeSlotAdmin(MaterialModelAdmin):
    list_display = ('start', 'end', 'time', 'allow',)
    list_filter = ('allow',)
    # list_editable = ('allow',)
    list_per_page = 10


class OrderAdmin(MaterialModelAdmin):
    list_filter = ('home_delivery', 'delivery_place', 'delivery_date_time', 'id',)
    # list_display = ('id','user','order_status', 'home_delivery')
    readonly_fields = ['created_by', 'modified_by', 'created_on', ]

    def _products(self, obj):
        return obj.offerproduct_set.all().count()

    def order_products(self):
        list = []
        objs = OrderProduct.objects.filter(order__id=self.id)
        for obj in objs:
            # html += "<p> <a href='%s'>%s</a></p>" %(obj.get_offer_product_url(),obj.product) # this code has been added to show hyperlink tag of offerproducts , but not rendering the html
            list.append('%s' % obj.product)
        return list

    list_display = ('id', 'user', 'order_status', 'home_delivery', 'delivery_date_time', order_products,)

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class OrderProductAdmin(MaterialModelAdmin):
    list_display = ('product', 'order_id', 'order_product_price', 'order_product_qty')
    list_filter = ('order',)
    readonly_fields = ['created_by', 'modified_by', 'created_on']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class VatAdmin(MaterialModelAdmin):
    list_display = ('id', 'vat_amount')
    list_filter = ('product_meta',)
    readonly_fields = ['created_by', 'modified_by', 'created_on']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class DeliveryChargeAdmin(MaterialModelAdmin):
    list_display = ['id', 'delivery_charge_inside_dhaka']
    list_filter = ['delivery_charge_inside_dhaka']
    readonly_fields = ['created_by', 'modified_by', 'delivery_charge_outside_dhaka', 'created_on']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


# class PaymentInfoAdmin(MaterialModelAdmin):
#     list_display = ['id', 'payment_id', 'order', 'payment_type']
# list_filter = ['delivery_charge_inside_dhaka']
# readonly_fields = ['created_by', 'modified_by','delivery_charge_outside_dhaka','created_on']

# def save_model(self, request, obj, form, change):
#     if obj.id:
#         obj.modified_by = request.user
#     obj.created_by = request.user
#     obj.save()
#     return super().save_model(request, obj, form, change)


class PaymentInfoAdmin(MaterialModelAdmin):
    list_display = ['id', 'payment_id', 'order', 'bill_id', 'invoice_number', 'payment_status', 'transaction_id']
    list_filter = ['order']
    readonly_fields = ['create_on']


def save_model(self, request, obj, form, change):
    if obj.id:
        obj.modified_by = request.user
    obj.created_by = request.user
    obj.save()
    return super().save_model(request, obj, form, change)


site.register(TimeSlot, TimeSlotAdmin)
site.register(Order, OrderAdmin)
site.register(OrderProduct, OrderProductAdmin)
site.register(Vat, VatAdmin)
site.register(DeliveryCharge, DeliveryChargeAdmin)
site.register(PaymentInfo, PaymentInfoAdmin)
