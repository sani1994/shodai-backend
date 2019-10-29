from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from offer.models import Offer,OfferProduct
# Register your models here.

class OfferAdmin(MaterialModelAdmin):
    icon_name='face'

class OfferProductAdmin(MaterialModelAdmin):
    fields = ('offer','product','offer_price','offer_product_balance')
    icon_name = 'face'

site.register(Offer,OfferAdmin)
site.register(OfferProduct,OfferProductAdmin)