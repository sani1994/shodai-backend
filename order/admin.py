import csv
import datetime

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from order.models import Order, Vat, OrderProduct, DeliveryCharge, PaymentInfo, TimeSlot, InvoiceInfo


# Register your models here.

class TimeSlotAdmin(MaterialModelAdmin):
    list_display = ('slot', 'start', 'end', 'time', 'allow')
    list_filter = ('allow',)
    list_per_page = 10
    readonly_fields = ['slot']


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    fields = ['product', 'order_product_qty', 'order_product_price']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class InvoiceInfoInline(admin.TabularInline):
    model = InvoiceInfo
    readonly_fields = ['invoice_number']
    fields = ['invoice_number', 'paid_status', 'payment_method']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderAdmin(MaterialModelAdmin):
    list_filter = ('home_delivery', 'delivery_place', 'delivery_date_time', 'id',)

    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        field_names = ['id', 'user', 'invoice_number', 'order_total_price',
                       'delivery_date_time', 'delivery_place', 'address',
                       'order_product_name', 'order_product_unit', 'order_product_quantity']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=order.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])
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
    inlines = [OrderProductInline, InvoiceInfoInline]
    fieldsets = (
        ('Order Detail View', {
            'fields': ('user', 'invoice_number', 'order_total_price', 'delivery_date_time', 'delivery_place',
                       'address')
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

    list_display = ('product', 'order_id', 'order_product_price', 'order_product_qty',
                    order_date)
    list_filter = ('order', 'order__delivery_date_time',)
    readonly_fields = ['product', 'order', 'order_product_price', 'order_product_price_with_vat', 'vat_amount',
                       'order_product_qty', 'created_by', 'modified_by', 'created_on']
    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        field_names = ['id', 'product', 'order', 'order_product_price',
                       'order_product_price_with_vat', 'vat_amount', 'order_product_qty', 'order_product_unit', ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=order_product.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = "Export Selected"

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

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class PaymentInfoAdmin(MaterialModelAdmin):
    list_display = ['id', 'payment_id', 'order_id', 'bill_id', 'invoice_number', 'payment_status', 'transaction_id']
    list_filter = ['order_id']
    readonly_fields = ['id', 'create_on', 'payment_id', 'order_id', 'bill_id', 'invoice_number',
                       'payment_status', 'transaction_id']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class InvoiceInfoAdmin(MaterialModelAdmin):
    list_display = ['id', 'invoice_number', 'order_number', 'delivery_date_time',
                    'paid_status', ]

    list_filter = ['created_on', 'delivery_date_time']
    # readonly_fields = ['created_on', 'created_by', 'modified_by', 'user', 'net_payable_amount',
    #                    'order_number', 'billing_person_mobile_number', 'delivery_date_time',
    #                    'delivery_contact_number', 'invoice_number', 'transaction_id']

    fieldsets = (
        ('Order Detail View', {
            'fields': ('invoice_number', 'order_number', 'net_payable_amount', 'delivery_date_time',
                       'discount_amount', 'discount_description', 'paid_status', 'payment_method',
                       'currency', 'transaction_id', 'delivery_contact_number',
                       'created_on', 'created_by', 'modified_by')
        }),
        ('User Detail View', {
            'fields': ('user', 'billing_person_name', 'billing_person_email', 'billing_person_mobile_number',
                       'delivery_address',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_on', 'created_by', 'modified_by', 'user', 'net_payable_amount',
                    'order_number', 'billing_person_name', 'billing_person_email', 'currency',
                    'billing_person_mobile_number', 'delivery_date_time', 'delivery_address'
                    'delivery_contact_number', 'invoice_number', 'transaction_id']
        else:
            return []

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
site.register(InvoiceInfo, InvoiceInfoAdmin)
