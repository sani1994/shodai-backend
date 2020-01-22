from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from order.models import Order,Vat,OrderProduct

# Register your models here.


class OrderAdmin(MaterialModelAdmin):
    list_filter = ('home_delivery', 'delivery_place', 'delivery_date_time', 'user_id')
    list_display = ('user','order_status', 'home_delivery')
    readonly_fields = ['created_by', 'modified_by','user']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class OrderProductAdmin(MaterialModelAdmin):
    list_display = ('product', 'order', 'order_product_price','order_product_qty')
    list_filter = ('order',)
    readonly_fields = ['created_by', 'modified_by']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class VatAdmin(MaterialModelAdmin):
    list_display = ('product_meta','vat_amount')
    list_filter = ('product_meta',)
    readonly_fields = ['created_by', 'modified_by']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)
        

site.register(Order, OrderAdmin)
site.register(OrderProduct,OrderProductAdmin)
site.register(Vat,VatAdmin)
