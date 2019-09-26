from django.contrib import admin
from producer.models import ProducerProduct, ProducerFarm

# Register your models here.

class ProducerProductAdmin(admin.ModelAdmin):
    # list_filter = ('product_name', 'product_unit', 'product_price', 'product_meta')
    list_display = ('product', 'product_time', 'amount_of_product')
    exclude = ['created_by', 'modified_by']

class ProducerFarmAdmin(admin.ModelAdmin):
    list_display = ('land_amount', 'type_of_crops_produce', 'product_photo', 'address')
    exclude = ['created_by', 'modified_by']

    

    def save_model(self, request, obj, form, change):
        print(obj.pk)
        if obj.pk == None: 
            print("inside None")
            obj.created_by = request.user
            obj.modified_by = request.user
        super().save_model(request,obj, form, change)

    def __str__(self):
        return str('%s object' % self.__class__.__name__)

        

admin.site.register(ProducerProduct, ProducerProductAdmin)