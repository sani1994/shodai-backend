from django.contrib import admin
from retailer.models import  Account
from userProfile.models import UserProfile
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from retailer.models import Account,Shop,AcceptedOrder

# Register your models here.

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

#     def save_model(self, request, obj, form, change):
#         print(obj.pk)
#         if obj.pk == None:
#             print("inside None")
#             obj.created_by = request.user
#             obj.modified_by = request.user
#         super().save_model(request,obj, form, change)
#
# # admin.site.unregister(Retailer)
# # admin.site.register(Retailer, RetailerAdmin)
# admin.site.register(RetailerAdmin)

class ShopAdmin(MaterialModelAdmin):
    pass
    # icon_name = 'perm_identity'


site.register(Shop)
site.register(Account)
site.register(AcceptedOrder)

