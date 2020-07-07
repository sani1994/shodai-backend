from django.contrib import admin

# Register your models here.
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site

from customerService.models import CustomerQuery


class CustomerQueryAdmin(MaterialModelAdmin):
    list_display = ('subject', 'name', 'contact_number', 'email')
    list_filter = ('created_on',)
    list_per_page = 10
    readonly_fields = ['subject', 'name', 'contact_number', 'email', 'created_on', 'message']


site.register(CustomerQuery, CustomerQueryAdmin)
