import csv

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from order.models import Order, Vat, OrderProduct, DeliveryCharge, PaymentInfo, TimeSlot


# Register your models here.

class TimeSlotAdmin(MaterialModelAdmin):
    list_display = ('start', 'end', 'time', 'allow', 'slot')
    list_filter = ('allow',)
    list_per_page = 10


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    fields = ['product', 'order_product_qty', 'order_product_price']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrderAdmin(MaterialModelAdmin):
    list_filter = ('home_delivery', 'delivery_place', 'delivery_date_time', 'id',)

    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        field_names = ['id', 'user', 'invoice_number', 'order_total_price',
                       'delivery_date_time', 'delivery_place', 'address']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=order.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow(
                [getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = "Export Selected"

    def _products(self, obj):
        return obj.offerproduct_set.all().count()

    def order_products(self):
        list = []
        objs = OrderProduct.objects.filter(order__id=self.id)
        for obj in objs:
            # html += "<p> <a href='%s'>%s</a></p>" %(obj.get_offer_product_url(),obj.product) # this code has been added to show hyperlink tag of offerproducts , but not rendering the html
            list.append('%s' % obj.product)
        return list

    readonly_fields = ['user', 'invoice_number', 'order_total_price',
                       'delivery_date_time', 'delivery_place', 'address', order_products]
    list_display = ('id', 'user', 'order_status', 'home_delivery', 'delivery_date_time', order_products,)
    inlines = [OrderProductInline]
    fieldsets = (
        ('Order Detail View', {
            'fields': ('user', 'invoice_number', 'order_total_price', 'delivery_date_time', 'delivery_place', 'address')
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class OrderProductAdmin(MaterialModelAdmin):
    def order_date(self):
        dates = []
        objs = Order.objects.filter(pk=self.order.id)
        for obj in objs:
            date, time = str(obj.delivery_date_time).split(' ', 1)
            dates.append('%s' % date)
        return dates

    list_display = (
        'product', 'order_id', 'order_product_price', 'order_product_price_with_vat', 'order_product_qty',
        order_date)
    list_filter = ('order',)
    readonly_fields = ['product', 'order', 'order_product_price', 'order_product_price_with_vat', 'vat_amount',
                       'order_product_qty', 'created_by', 'modified_by', 'created_on']

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


class PaymentInfoAdmin(MaterialModelAdmin):
    list_display = ['id', 'payment_id', 'order_id', 'bill_id', 'invoice_number', 'payment_status', 'transaction_id']
    list_filter = ['order_id']
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
