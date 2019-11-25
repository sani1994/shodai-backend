from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site

# Register your models here.
from utility.models import Area, CityCountry, Location, ProductUnit, CommissionRate, Remarks

site.register(Area)
site.register(CityCountry)
site.register(Location)
site.register(ProductUnit)
site.register(CommissionRate)
site.register(Remarks)
