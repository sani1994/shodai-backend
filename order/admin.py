from django.contrib import admin
from order.models import Order

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_filter = ('home_delivery', 'delivery_place', 'delivery_date_time', 'user_id')
    list_display = ('user_id','delivery_date_time', 'delivery_place', 'order_status', 'home_delivery', 'created_by', 'modified_by')
    exclude = ['created_by', 'modified_by']
    def save_model(self, request, obj, form, change):
        print(obj.pk)
        if obj.pk == None: 
            print("inside None")
            obj.created_by = request.user
            obj.modified_by = request.user
        super().save_model(request,obj, form, change)
        

admin.site.register(Order, OrderAdmin)

# admin.site.register(OrderProduct)
# admin.site.register(Vat)