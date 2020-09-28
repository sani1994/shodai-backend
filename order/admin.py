import csv
import datetime

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from num2words import num2words

from order.models import Order, Vat, OrderProduct, DeliveryCharge, PaymentInfo, TimeSlot, InvoiceInfo

# Register your models here.
from utility.pdf import render_to_pdf


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
    fields = ['invoice_number', 'paid_status', 'payment_method']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrderAdmin(MaterialModelAdmin):
    list_filter = ('home_delivery', 'delivery_place', 'delivery_date_time', 'id',)

    actions = ["export_as_csv"]
    change_form_template = "order_admin_changeform.html"

    def response_change(self, request, obj):
        if "_download-pdf" in request.POST:
            product_list = OrderProduct.objects.filter(order__pk=obj.id)
            matrix = []
            total_vat = 0
            for p in product_list:
                total = float(p.product.product_price) * p.order_product_qty
                col = [p.product.product_name, p.product.product_unit.product_unit, p.order_product_qty,
                       p.product.product_price, total]
                matrix.append(col)
                vat = p.order_product_price_with_vat * p.order_product_qty - total
                total_vat += vat
            invoice = InvoiceInfo.objects.filter(invoice_number=obj.invoice_number)[0].payment_method
            if invoice == "CASH_ON_DELIVERY":
                payment_method = "Cash on Delivery"
            elif invoice == "SSLCOMMERZ":
                payment_method = "Online Payment"
            data = {
                'customer_name': obj.user.first_name + " " + obj.user.last_name,
                'address': obj.address,
                'user_email': obj.user.email,
                'user_mobile': obj.user.mobile_number,
                'order_id': obj.id,
                'invoice_number': obj.invoice_number,
                'created_on': obj.created_on,
                'delivery_date': obj.delivery_date_time.date(),
                'delivery_time': obj.delivery_date_time.time(),
                'order_details': matrix,
                'delivery': DeliveryCharge.objects.get().delivery_charge_inside_dhaka,
                'vat': total_vat,
                'total': obj.order_total_price,
                'in_words': num2words(obj.order_total_price),
                'payment_method': payment_method
            }
            pdf = render_to_pdf('pdf/invoice.html', data)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Invoice_of_order#%s.pdf" % obj.id
                # content = "inline; filename=%s" % filename
                # download = request.GET.get("download")
                # if download:
                content = "attachment; filename=%s" % filename
                response['Content-Disposition'] = content
                return response
            return HttpResponse("Not found")
        return super().response_change(request, obj)

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

    readonly_fields = ['user', 'invoice_number', 'order_total_price', 'created_by', 'modified_by', 'created_on',
                       'modified_on', 'delivery_date_time', 'delivery_place', 'address', order_products]
    list_display = ('id', 'user', 'order_status', 'invoice_number', 'delivery_date_time', order_products,)
    list_editable = ('order_status',)
    search_fields = ['id', 'invoice_number']
    inlines = [OrderProductInline, InvoiceInfoInline]
    fieldsets = (
        ('Order Detail View', {
            'fields': ('user', 'invoice_number', 'order_total_price', 'order_status', 'delivery_date_time',
                       'delivery_place', 'address', 'created_by', 'modified_by', 'created_on', 'modified_on')
        }),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
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

    def has_delete_permission(self, request, obj=None):
        return False

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
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class InvoiceInfoAdmin(MaterialModelAdmin):
    list_display = ['id', 'invoice_number', 'order_number', 'paid_status', 'paid_on']

    search_fields = ['invoice_number', 'order_number__pk']
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

    def export_as_csv(self, request, queryset):
        field_names = ['id', 'invoice_number', 'order_number', 'net_payable_amount', 'payment_method',
                       'paid_status', 'paid_on', 'transaction_id', 'created_on', ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=invoice_report.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])
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


site.register(TimeSlot, TimeSlotAdmin)
site.register(Order, OrderAdmin)
site.register(OrderProduct, OrderProductAdmin)
site.register(Vat, VatAdmin)
site.register(DeliveryCharge, DeliveryChargeAdmin)
site.register(PaymentInfo, PaymentInfoAdmin)
site.register(InvoiceInfo, InvoiceInfoAdmin)
