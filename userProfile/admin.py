from django.contrib import admin
from userProfile.models import UserProfile, Address

# Register your models here.

class AddressAdmin(admin.ModelAdmin):
    list_display = ('road' , 'city', 'district', 'country')

class AddressInline(admin.StackedInline):
    """ Details a person in line. """
    model = Address
    can_delete = False
    verbose_name_plural = 'person'

    fields = ('road', 'city', 'district')


    

# class UserInfoAdmin(admin.ModelAdmin):
#     # list_display = ('mobile_number', 'user_id', 'address')
#     # exclude = ['created_by', 'modified_by']

#     # inlines = [
#     #     AddressInline 
#     # ]
#     list_display = ['retailer_user', 'address']

admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
# admin.site.register(UserInfo, UserInfoAdmin)

# admin.site.register(Retailer, RetailerAdmin)