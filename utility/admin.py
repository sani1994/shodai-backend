from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from utility.models import Area, CityCountry, Location, ProductUnit, Remarks, Message


class AreaAdmin(MaterialModelAdmin):
    pass


class CityCountryAdmin(MaterialModelAdmin):
    pass


class LocationAdmin(MaterialModelAdmin):
    pass


class ProductUnitAdmin(MaterialModelAdmin):
    list_display = ('id', 'product_unit',)
    list_filter = ('product_unit',)
    readonly_fields = ["created_by", "modified_by", ]
    search_fields = ['product_unit']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class RemarksAdmin(MaterialModelAdmin):
    pass


class MessageAdmin(MaterialModelAdmin):
    list_display = ('message', 'screen_name')
    readonly_fields = ["created_by", "modified_by", ]


site.register(Area, AreaAdmin)
site.register(CityCountry, CityCountryAdmin)
site.register(Location, LocationAdmin)
site.register(ProductUnit, ProductUnitAdmin)
site.register(Remarks)
site.register(Message, MessageAdmin)
