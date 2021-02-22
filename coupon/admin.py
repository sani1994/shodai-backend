from django.contrib import admin

# Register your models here.
from django.utils import timezone
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site

from coupon.models import CouponCode, CouponUser, CouponUsageHistory


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
    list_display = ['id', 'name', 'discount_percent', 'discount_amount', 'expiry_date']
    list_filter = ['created_on', 'expiry_date']

    inlines = [CouponUserInline]
    fieldsets = (
        ('Coupon Detail View', {
            'fields': ('name', 'coupon_code', 'discount_type', 'discount_percent', 'discount_amount',
                       'discount_amount_limit', 'expiry_date', 'created_by', 'modified_by', 'created_on',
                       'modified_on',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['name', 'coupon_code', 'discount_percent', 'discount_amount', 'discount_amount_limit',
                    'discount_type', 'expiry_date', 'created_by', 'modified_by', 'created_on', 'modified_on']
        else:
            return ['created_on', 'modified_on', 'created_by', 'modified_by']

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


site.register(CouponCode, CouponCodeAdmin)
site.register(CouponUsageHistory, CouponUsageHistoryAdmin)
