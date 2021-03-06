from django.contrib import admin

# Register your models here.
from django.utils import timezone
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site

from coupon.models import CouponCode, CouponUser, CouponUsageHistory, CouponSettings


class CouponUserInline(admin.TabularInline):
    model = CouponUser
    fields = ['created_for', 'remaining_usage_count']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CouponCodeAdmin(MaterialModelAdmin):
    list_display = ['id', 'coupon_code', 'name', 'discount_percent', 'discount_amount', 'created_on', 'expiry_date']
    list_filter = ['created_on', 'expiry_date', 'coupon_code_type']
    search_fields = ['coupon_code', 'created_by__mobile_number']

    inlines = [CouponUserInline]
    fieldsets = (
        ('Coupon Detail View', {
            'fields': ('name', 'coupon_code', 'coupon_code_type', 'discount_type', 'discount_amount',
                       'minimum_purchase_limit', 'discount_percent', 'discount_amount_limit', 'expiry_date',
                       'created_by', 'modified_by', 'created_on', 'modified_on',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            field_list = ['name', 'coupon_code', 'coupon_code_type', 'discount_type', 'discount_percent',
                          'minimum_purchase_limit', 'discount_amount', 'discount_amount_limit', 'expiry_date',
                          'created_by', 'modified_by', 'created_on', 'modified_on']
            if obj.coupon_code_type == 'PC':
                field_list.remove('expiry_date')
            return field_list
        else:
            return ['coupon_code_type', 'created_on', 'modified_on', 'created_by', 'modified_by']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
            obj.modified_on = timezone.now()
        else:
            obj.created_by = request.user
            obj.created_on = timezone.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


class CouponUsageHistoryAdmin(MaterialModelAdmin):
    list_display = ['id', 'coupon_code', 'coupon_user', 'invoice_number']
    list_filter = ['created_on']
    search_fields = ['coupon_code', 'coupon_user__created_for__mobile_number',
                     'invoice_number__order_number__order_number']

    fieldsets = (
        ('Coupon Detail View', {
            'fields': ('coupon_code', 'coupon_user', 'invoice_number', 'discount_percent',
                       'discount_amount', 'discount_type', 'created_by', 'modified_by', 'created_on', 'modified_on')
        }),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CouponSettingsAdmin(MaterialModelAdmin):
    list_display = ['coupon_type', 'discount_percent', 'discount_amount',
                    'validity_period', 'is_active']

    fieldsets = (
        ('Coupon Detail View', {
            'fields': ('coupon_type', 'discount_type', 'discount_percent', 'discount_amount', 'discount_amount_limit',
                       'minimum_purchase_limit', 'max_usage_count', 'validity_period', 'is_active',
                       'modified_by', 'modified_on')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj.coupon_type == 'RC':
            return ['coupon_type', 'modified_by', 'modified_on']
        else:
            return ['coupon_type', 'max_usage_count', 'modified_on', 'modified_by']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
            obj.modified_on = timezone.now()
        obj.save()


site.register(CouponCode, CouponCodeAdmin)
site.register(CouponUsageHistory, CouponUsageHistoryAdmin)
site.register(CouponSettings, CouponSettingsAdmin)
