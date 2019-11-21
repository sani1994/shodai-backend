from builtins import super

from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from product.models import ShopCategory, ProductCategory, ProductMeta, ProductUnit,Product
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_filter = ('product_name', 'product_meta','is_approved')
    list_display = ('product_name','product_price','is_approved')
    read_only = ['created_by', 'modified_by']

    def save_model(self, request, obj, form, change):
        if obj.pk == None:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request,obj, form, change)


class ProductUnitResource(resources.ModelResource):

    class Meta:
        model = ProductUnit
        fields = ('id','product_unit')


class ProductUnitAdmin(ImportExportModelAdmin):
    list_display = ('product_unit','history')
    resource_class = ProductUnitResource

    def save_model(self, request, obj, form, change):
        if obj.pk == None:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request,obj, form, change)


class ShopCategoryResource(resources.ModelResource):

    class Meta:
        model = ShopCategory
        fields = ('id','type_of_shop')


class ShopCategoryAdmin(ImportExportModelAdmin):
    list_display=('type_of_shop','created_by')
    readonly_fields = ["created_by", "modified_by",]
    resource_class = ShopCategoryResource

    def save_model(self, request, obj, form, change):
            if not obj.pk:
                obj.created_by = request.user
            obj.modified_by = request.user
            return super().save_model(request,obj, form, change)


site.register(Product, ProductAdmin)
site.register(ShopCategory,ShopCategoryAdmin)
site.register(ProductCategory)
site.register(ProductMeta)
site.register(ProductUnit,ProductUnitAdmin)
