from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from utility.models import Area, CityCountry, Location, ProductUnit, Remarks, Message, Banner, DeliveryZone, \
    QurbaniProductCriteria


class AreaAdmin(MaterialModelAdmin):
    pass


class CityCountryAdmin(MaterialModelAdmin):
    pass


class LocationAdmin(MaterialModelAdmin):
    pass


class DeliveryZoneAdmin(MaterialModelAdmin):
    list_display = ["id", "zone"]
    readonly_fields = ["modified_by", "modified_on", "created_by", "created_on"]
    search_fields = ["zone"]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


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

    def has_delete_permission(self, request, obj=None):
        return False


class BannerAdmin(MaterialModelAdmin):
    list_display = ('banner_heading', 'banner_show_starts_in', 'banner_show_ends_in', 'is_approved')
    list_filter = ('banner_show_starts_in', 'banner_show_ends_in', )
    readonly_fields = ["created_by", "modified_by", "created_on", "modified_on", ]
    search_fields = ['banner_heading']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


class RemarksAdmin(MaterialModelAdmin):
    pass


class MessageAdmin(MaterialModelAdmin):
    list_display = ('message', 'screen_name')
    readonly_fields = ["created_by", "modified_by", ]


class QurbaniProductCriteriaAdmin(MaterialModelAdmin):
    list_display = ["id", "pre_order_setting", "category", "breed", "color", "teeth"]
    readonly_fields = ["modified_by", "modified_on", "created_by", "created_on"]
    search_fields = ["pre_order_setting__producer_product__product_name"]
    autocomplete_fields = ["pre_order_setting"]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


site.register(Area, AreaAdmin)
site.register(CityCountry, CityCountryAdmin)
site.register(Location, LocationAdmin)
site.register(ProductUnit, ProductUnitAdmin)
site.register(Remarks)
site.register(Message, MessageAdmin)
site.register(Banner, BannerAdmin)
site.register(DeliveryZone, DeliveryZoneAdmin)
site.register(QurbaniProductCriteria, QurbaniProductCriteriaAdmin)
