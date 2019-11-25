from django.contrib import admin
from material.admin.sites import site

# Register your models here.
from inventory.models import ShopInventory

site.register(ShopInventory)