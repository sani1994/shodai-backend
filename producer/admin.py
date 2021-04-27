from builtins import super

from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site


# Register your models here.

class ProducerBulkRequestAdmin(MaterialModelAdmin):
    list_display = ('product_name', )
    readonly_fields = ['created_by', 'modified_by', 'user', 'created_on']

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

# site.register(ProducerBulkRequest, ProducerBulkRequestAdmin)
# site.register(ProducerFarm, ProducerFarmAdmin)
# site.register(BusinessType, BusinessTypeAdmin)
# site.register(ProducerBusiness, ProducerBusinessAdmin)
