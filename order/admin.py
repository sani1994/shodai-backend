import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from order.models import Order, Vat, OrderProduct, DeliveryCharge, PaymentInfo, TimeSlot, InvoiceInfo, DiscountInfo, \
    PreOrderSetting


# Register your models here.


class TimeSlotAdmin(MaterialModelAdmin):
    list_display = ('slot', 'start', 'end', 'time', 'allow')
    list_filter = ('allow',)
    list_per_page = 10
    readonly_fields = ['slot']

    def has_delete_permission(self, request, obj=None):
        return False


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    fields = ['product', 'product_price', 'order_product_price', 'order_product_qty', 'order_product_total_price']
    readonly_fields = ['product', 'product_price', 'order_product_price', 'order_product_qty',
                       'order_product_total_price']

    def order_product_total_price(self, obj):
        return obj.order_product_price * obj.order_product_qty

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class InvoiceInfoInline(admin.TabularInline):
    model = InvoiceInfo
    fields = ['invoice_number', 'paid_status', 'payment_method', 'discount_amount']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrderAdmin(MaterialModelAdmin):
    list_filter = ('home_delivery', 'delivery_place', 'delivery_date_time', 'id',)

    actions = ["export_as_csv"]

    # change_form_template = "order_admin_changeform.html"

    def get_actions(self, request):
        actions = super(OrderAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            return []
        else:
            return actions

    def export_as_csv(self, request, queryset):
        field_names = ['ID', 'Customer', 'Invoice Number', 'Order Total Price',
                       'Delivery Date Time', 'Delivery Place', 'Address',
                       'Product Name', 'Product Unit', 'Product Quantity']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=order.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([obj.id, obj.user.mobile_number, obj.invoice_number, obj.order_total_price,
                             obj.delivery_date_time, obj.delivery_place, obj.address, obj.order_product_name,
                             obj.order_product_unit, obj.order_product_quantity])
        return response

    export_as_csv.short_description = "Export Selected"

    def order_products(self):
        list = []
        objs = OrderProduct.objects.filter(order__id=self.id)
        for obj in objs:
            list.append('%s' % obj.product)
        return list

    readonly_fields = ['user', 'invoice_number', 'order_number', 'order_total_price', 'created_by', 'modified_by',
                       'created_on', 'modified_on', 'delivery_date_time', 'delivery_place', 'address', 'note',
                       'total_vat', order_products, 'order_status', 'platform']
    list_display = (
    'id', 'order_number', 'user', 'order_status', 'invoice_number', 'delivery_date_time', order_products)
    search_fields = ['id', 'invoice_number', 'order_number', 'user__mobile_number']
    inlines = [OrderProductInline, InvoiceInfoInline]
    fieldsets = (
        ('Order Detail View', {
            'fields': (
            'user', 'platform', 'invoice_number', 'order_number', 'total_vat', 'order_total_price', 'order_status',
            'delivery_date_time',
            'delivery_place', 'address', 'note', 'created_by', 'modified_by', 'created_on', 'modified_on')
        }),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
    readonly_fields = ['product', 'product_price', 'order', 'order_product_price', 'order_product_price_with_vat',
                       'vat_amount',
                       'order_product_qty', 'created_by', 'modified_by', 'created_on']
    actions = ["export_as_csv"]

    def get_actions(self, request):
        actions = super(OrderProductAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            return []
        else:
            return actions

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

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
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
        else:
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
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class PaymentInfoAdmin(MaterialModelAdmin):
    list_display = ['id', 'order_id', 'invoice_number', 'payment_status', 'transaction_id']
    list_filter = ['order_id']
    readonly_fields = ['id', 'order_id', 'invoice_number', 'payment_status', 'transaction_id',
                       'bill_id', 'payment_id', 'create_on']
    search_fields = ['transaction_id', 'order_id__pk', 'invoice_number']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class DiscountInfoInline(admin.TabularInline):
    model = DiscountInfo
    fields = ['discount_amount', 'discount_type', 'discount_description']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class InvoiceInfoAdmin(MaterialModelAdmin):
    list_display = ['id', 'invoice_number', 'order_number', 'paid_status', 'paid_on']

    search_fields = ['invoice_number', 'order_number__order_number']
    list_filter = ['created_on', 'delivery_date_time', 'payment_method', 'paid_status']

    fieldsets = (
        ('Order Detail View', {
            'fields': ('invoice_number', 'order_number', 'delivery_charge', 'discount_amount', 'currency',
                       'discount_description', 'net_payable_amount', 'delivery_date_time',)
        }),
        ('User Detail View', {
            'fields': ('user', 'billing_person_name', 'billing_person_email', 'billing_person_mobile_number',
                       'delivery_address', 'delivery_contact_number')
        }),
        ('Invoice Detail View', {
            'fields': ('paid_status', 'payment_method', 'transaction_id', 'created_on', 'modified_on', 'paid_on',
                       'created_by', 'modified_by')
        }),
    )

    actions = ["export_as_csv"]
    inlines = [DiscountInfoInline]

    def get_actions(self, request):
        actions = super(InvoiceInfoAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            return []
        else:
            return actions

    def export_as_csv(self, request, queryset):
        field_names = ['id', 'invoice_number', 'order_number', 'net_payable_amount', 'payment_method',
                       'paid_status', 'paid_on', 'transaction_id', 'created_on', ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=invoice_report.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = "Export Selected"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['invoice_number', 'order_number', 'delivery_charge', 'discount_amount', 'currency',
                    'discount_description', 'net_payable_amount', 'created_on', 'created_by', 'modified_by',
                    'user', 'billing_person_name', 'billing_person_email', 'billing_person_mobile_number',
                    'delivery_address', 'delivery_contact_number', 'delivery_date_time', 'modified_on',
                    'transaction_id', 'paid_on']
        else:
            return ['created_on', 'modified_on', 'created_by', 'modified_by']

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if obj:
            if obj.id:
                obj.modified_by = request.user
            if obj.paid_status:
                obj.paid_on = timezone.now()
                obj.save()
            else:
                obj.paid_on = None
                obj.save()
            obj.save()
            return super().save_model(request, obj, form, change)
        else:
            if obj.id:
                obj.modified_by = request.user
            obj.created_by = request.user
            obj.created_on = timezone.now()
            if obj.paid_status:
                obj.paid_on = timezone.now()
                obj.save()
            obj.save()
            return super().save_model(request, obj, form, change)


class DiscountInfoAdmin(MaterialModelAdmin):
    list_display = ['id', 'discount_amount', 'discount_type', 'invoice']

    search_fields = ['invoice__invoice_number', 'invoice__order_number__order_number']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class PreOrderSettingAdmin(MaterialModelAdmin):
    list_display = ('product', 'start_date', 'end_date', 'is_approved')
    readonly_fields = ['created_by', 'modified_by', 'created_on', 'modified_on', 'slug']
    autocomplete_fields = ['product']

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
site.register(DiscountInfo, DiscountInfoAdmin)
site.register(PreOrderSetting, PreOrderSettingAdmin)
