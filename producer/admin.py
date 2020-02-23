from builtins import super

from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from producer.models import ProducerBulkRequest, ProducerFarm, ProducerBusiness, BusinessType, BulkOrderReqConnector, \
    MicroBulkOrderProducts, MicroBulkOrder, BulkOrderProducts, BulkOrder


# Register your models here.

class ProducerBulkRequestAdmin(MaterialModelAdmin):
    list_filter = ('product_name', 'product_category')
    list_display = ('product_name', 'product_category', 'production_time', 'unit_price')
    readonly_fields = ['created_by', 'modified_by', 'user', 'created_on']

    class Meta:
        verbose_name_plural = "producer products"

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
            obj.save()
        obj.created_by = request.user
        obj.user = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class ProducerFarmAdmin(MaterialModelAdmin):
    list_display = ('land_amount', 'type_of_crops_produce', 'product_photo', 'address')
    readonly_fields = ['created_by', 'modified_by']

    # def save_model(self, request, obj, form, change):
    #     print(obj.pk)
    #     if obj.pk == None:
    #         print("inside None")
    #         obj.created_by = request.user
    #         obj.modified_by = request.user
    #     super().save_model(request,obj, form, change)

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)

    def __str__(self):
        return str('%s object' % self.__class__.__name__)


class BusinessTypeAdmin(MaterialModelAdmin):
    pass


class ProducerBusinessAdmin(MaterialModelAdmin):
    pass


class BulkOrderAdmin(MaterialModelAdmin):
    list_display = ('user', 'start_date', 'expire_date')
    list_filter = ('hex_code',)
    readonly_fields = ['created_by', 'modified_by', 'user', 'created_on']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.user = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class BulkOrderProductsAdmin(MaterialModelAdmin):
    list_display = ('product', 'bulk_order')
    list_filter = ('bulk_order',)
    readonly_fields = ['created_by', 'modified_by','created_on','available_qty']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class MicroBulkOrderAdmin(MaterialModelAdmin):
    list_display = ('customer', 'bulk_order')
    readonly_fields = ['created_by', 'modified_by', 'customer','created_on']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.customer = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class MicrobulkOrderProductAdmin(MaterialModelAdmin):
    list_display = ('micro_bulk_order','bulk_order_products')
    readonly_fields = ['created_by', 'modified_by', 'created_on']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


site.register(ProducerBulkRequest, ProducerBulkRequestAdmin)
site.register(ProducerFarm, ProducerFarmAdmin)
site.register(BusinessType, BusinessTypeAdmin)
site.register(ProducerBusiness, ProducerBusinessAdmin)
site.register(BulkOrder, BulkOrderAdmin)
site.register(BulkOrderProducts, BulkOrderProductsAdmin)
site.register(MicroBulkOrder, MicroBulkOrderAdmin)
site.register(MicroBulkOrderProducts,MicrobulkOrderProductAdmin)
site.register(BulkOrderReqConnector)
