from builtins import super

from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site

from producer.models import ProducerProductRequest


# Register your models here.

class ProducerProductRequestAdmin(MaterialModelAdmin):
    list_display = ('product_name', 'product_quantity', 'producer', 'is_approved')
    readonly_fields = ['created_by', 'modified_by', 'created_on', 'modified_on']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class ProducerFarmAdmin(MaterialModelAdmin):
    list_display = ('land_amount', 'type_of_crops_produce', 'product_photo', 'address')
    readonly_fields = ['created_by', 'modified_by', 'created_on']

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


site.register(ProducerProductRequest, ProducerProductRequestAdmin)
# site.register(ProducerFarm, ProducerFarmAdmin)
# site.register(BusinessType, BusinessTypeAdmin)
# site.register(ProducerBusiness, ProducerBusinessAdmin)
