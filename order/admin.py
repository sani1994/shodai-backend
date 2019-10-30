from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from order.models import Order,Vat,OrderProduct

# Register your models here.
class OrderAdmin(MaterialModelAdmin):
    list_filter = ('home_delivery', 'delivery_place', 'delivery_date_time', 'user_id')
    list_display = ('user_id','delivery_date_time', 'delivery_place', 'order_status', 'home_delivery', 'created_by', 'modified_by')
    exclude = ['created_by', 'modified_by']
    def save_model(self, request, obj, form, change):
        if obj.pk == None: 
            print("inside None")
            obj.created_by = request.user
            obj.modified_by = request.user
        super().save_model(request,obj, form, change)

class OrderProductAdmin(MaterialModelAdmin):
    pass
    # icon_name = 'order'

class VatAdmin(MaterialModelAdmin):
    # icon_name = 'order'
    pass
        

site.register(Order, OrderAdmin)
site.register(OrderProduct,OrderProductAdmin)
site.register(Vat)

# admin.site.register(OrderProduct)
# admin.site.register(Vat)