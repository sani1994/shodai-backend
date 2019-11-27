from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from offer.models import Offer,OfferProduct
# Register your models here.

class OfferAdmin(MaterialModelAdmin):
    pass
    # icon_name='face'

class OfferProductAdmin(MaterialModelAdmin):
    list_display = ('offer','product','offer_price','offer_product_balance','is_approved')
    list_filter = ('offer','product','is_approved')

site.register(Offer,app = __package__)
site.register(OfferProduct,OfferProductAdmin)