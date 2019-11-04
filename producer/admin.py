from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from producer.models import ProducerProduct, ProducerFarm

# Register your models here.

class ProducerProductAdmin(MaterialModelAdmin):
    # list_filter = ('product_name', 'product_unit', 'product_price', 'product_meta')
    list_display = ('product_name', 'product_image', 'product_category','production_time','unit_price','delivery_amount','created_by','modified_by')
    # exclude = ['created_by', 'modified_by']

class ProducerFarmAdmin(MaterialModelAdmin):
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

        

site.register(ProducerProduct, ProducerProductAdmin)
site.register(ProducerFarm,ProducerFarmAdmin)