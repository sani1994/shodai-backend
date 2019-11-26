from django.contrib import admin
from material.admin.sites import site

# Register your models here.
from market.models import WholeSellRate, KitchenMarket, CommissionRate

site.register(WholeSellRate)
site.register(KitchenMarket)
site.register(CommissionRate)

