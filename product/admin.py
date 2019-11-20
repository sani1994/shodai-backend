from builtins import super

from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from product.models import ShopCategory, ProductCategory, ProductMeta, ProductUnit,Product

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

class ProductUnitAdmin(admin.ModelAdmin):
    list_display = ('product_unit','history')

    def save_model(self, request, obj, form, change):
        if obj.pk == None:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request,obj, form, change)


class ShopCategoryAdmin(admin.ModelAdmin):
    list_display=('type_of_shop','created_by')
    readonly_fields = ["created_by", "modified_by",]

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
