from django.contrib import admin
from product.models import ShopCategory, ProductCategory, ProductMeta, Product

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_filter = ('product_name', 'product_unit', 'product_price', 'product_meta')
    list_display = ('product_name', 'product_unit', 'product_price', 'product_meta')
    exclude = ['created_by', 'modified_by']

    def save_model(self, request, obj, form, change):
        print(obj.pk)
        if obj.pk == None: 
            print("inside None")
            obj.created_by = request.user
            obj.modified_by = request.user
        super().save_model(request,obj, form, change)
        
    
admin.site.register(Product, ProductAdmin)