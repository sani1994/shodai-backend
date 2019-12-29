from django.contrib import admin
from retailer.models import  Account
from userProfile.models import UserProfile
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from retailer.models import Account,Shop,AcceptedOrder

# Register your models here.
#
# class UserInline(admin.StackedInline):
#     """ Details a person in line. """
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'person'
#
#     fields = ('email', 'first_name', 'last_name', 'city')
#
#
# class RetailerAdmin(admin.ModelAdmin):
#     list_display = ('user_id', 'user', 'address', 'retailer_email', 'retailer_website')
#     exclude = ['created_by', 'modified_by']
#     # inlines = [
#     #     UserInline
#     # ]
#
#     def save_model(self, request, obj, form, change):
#         print(obj.pk)
#         if obj.pk == None:
#             print("inside None")
#             obj.created_by = request.user
#             obj.modified_by = request.user
#         super().save_model(request,obj, form, change)

# admin.site.unregister(Retailer)
#
#
#
# admin.site.register(Retailer, RetailerAdmin)
# admin.site.register(RetailerAdmin)

class ShopAdmin(MaterialModelAdmin):
    model = Shop
    list_display = ('shop_name','is_approved')
    readonly_fields = ["created_by", "modified_by",'user']
    verbose_name = 'Shop'

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.user = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class AcceptedOrderAdmin(MaterialModelAdmin):
    model = AcceptedOrder
    list_display = ('order', 'user')
    readonly_fields = ["created_by", "modified_by", 'user','order','order_product']


site.register(Shop, ShopAdmin)
site.register(Account)
site.register(AcceptedOrder,AcceptedOrderAdmin)
# site.register(UserInline)

