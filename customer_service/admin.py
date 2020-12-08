from django.contrib import admin

# Register your models here.
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site

from customer_service.models import CustomerQuery


class CustomerQueryAdmin(MaterialModelAdmin):
    list_display = ('subject', 'name', 'contact_number', 'email', 'processed')
    list_filter = ('created_on',)
    list_per_page = 10
    readonly_fields = ['subject', 'name', 'contact_number', 'email', 'created_on', 'message']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


site.register(CustomerQuery, CustomerQueryAdmin)
