from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from offer.models import Offer,OfferProduct
# Register your models here.

class OfferAdmin(MaterialModelAdmin):
    icon_name='face'

site.register(Offer,OfferAdmin)
site.register(OfferProduct)