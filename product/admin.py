from builtins import super

from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from rest_framework.generics import get_object_or_404

from product.models import ShopCategory, ProductCategory, ProductMeta, Product
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Register your models here.

class ProductAdmin(MaterialModelAdmin):
    list_filter = ('product_name', 'product_meta', 'is_approved')
    list_display = ('id', 'product_name', 'product_price', 'price_with_vat', 'is_approved')
    readonly_fields = ["created_by", "modified_by", 'price_with_vat', 'slug']
    search_fields = ['product_name']
    autocomplete_fields = ('product_unit',)
    actions = ["save_selected"]

    def save_selected(self, request, queryset):
        for obj in queryset:
            obj.save()

    save_selected.short_description = "Save Selected"

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
            # old_obj = get_object_or_404(Product, id=obj.id)
            # obj.product_last_price = old_obj.product_price
            obj.save()
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class ProductUnitAdmin(ImportExportModelAdmin):
    list_display = ('product_unit', 'history')

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class ShopCategoryResource(resources.ModelResource):
    class Meta:
        model = ShopCategory
        fields = ('id', 'type_of_shop')


class ShopCategoryAdmin(ImportExportModelAdmin):
    list_display = ('type_of_shop', 'created_by')
    readonly_fields = ["created_by", "modified_by", ]
    resource_class = ShopCategoryResource

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class ProductCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "modified_by", ]
    list_display = ("type_of_product",)

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class ProductMetaAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "modified_by", ]
    list_display = ('id', 'name', 'product_category', 'shop_category', 'vat_amount')
    list_filter = ('product_category', 'shop_category')

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


site.register(Product, ProductAdmin)
site.register(ShopCategory, ShopCategoryAdmin)
site.register(ProductCategory, ProductCategoryAdmin)
site.register(ProductMeta, ProductMetaAdmin)
# site.register(ProductUnit, ProductUnitAdmin)
