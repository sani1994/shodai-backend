from django.contrib import admin
from django.contrib.admin import register
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from userProfile.models import UserProfile, Address, Otp

# Register your models here.

class AddressAdmin(MaterialModelAdmin):
    list_display = ('road' , 'city', 'district', 'country')
    # icon_name = 'address'

class UserProfileAdmin(MaterialModelAdmin):
    icon_name ='face'

class OtpAdmin(MaterialModelAdmin):
    pass
    # icon_name = 'otp'
# class AddressInline(admin.StackedInline):
#     """ Details a person in line. """
#     model = Address
#     can_delete = False
#     verbose_name_plural = 'person'
#
#     fields = ('road', 'city', 'district')




# class UserInfoAdmin(admin.ModelAdmin):
#     # list_display = ('mobile_number', 'user_id', 'address')
#     # exclude = ['created_by', 'modified_by']

#     # inlines = [
#     #     AddressInline
#     # ]
#     list_display = ['retailer_user', 'address']

# admin.site.register(Address, AddressAdmin)
# admin.site.register(UserProfile)
# admin.site.register(UserInfo, UserInfoAdmin)

# admin.site.register(Retailer, RetailerAdmin)
site.register(UserProfile,UserProfileAdmin)
site.register(Address,AddressAdmin)
site.register(Otp,OtpAdmin)
