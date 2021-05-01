from django.contrib import admin
from django.contrib.admin import register
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from simple_history.admin import SimpleHistoryAdmin

from user.models import UserProfile, Address, Otp


# Register your models here.

class AddressAdmin(MaterialModelAdmin):
    list_display = ('road', 'city', 'district', 'country')
    history_list_display = ["road"]
    # icon_name = 'address'


class UserProfileAdmin(MaterialModelAdmin):
    icon_name = 'face'
    list_display = ('mobile_number', 'user_type', 'first_name', 'last_name', 'created_on',
                    'is_approved')
    exclude = ['password', ]
    readonly_fields = ['created_on', 'modified_on', 'date_joined', 'last_login']
    search_fields = ['mobile_number', 'first_name', 'last_name']
    fieldsets = (
        ('User Detail View', {
            'fields': (
                'mobile_number', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'groups',
                'user_permissions', 'is_staff', 'is_active', 'user_NID', 'user_type',
                'verification_code', 'code_valid_till', 'pin_verified', 'date_joined',
                'last_login', 'created_on', 'modified_on', 'is_approved', 'is_customer'
                )
        }),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        # obj.user = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


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
site.register(UserProfile, UserProfileAdmin)
site.register(Address, AddressAdmin)
site.register(Otp, OtpAdmin)
