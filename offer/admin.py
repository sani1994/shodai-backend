from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from offer.models import Offer,OfferProduct
# Register your models here.


class OfferAdmin(MaterialModelAdmin):
    list_filter = ('offer_name','offer_starts_in','offer_ends_in','is_approved')
    readonly_fields = ["created_by", "modified_by", ]


    def _products(self,obj):
        return obj.offerproduct_set.all().count()


    def offer_products(self):
        list = []
        objs = OfferProduct.objects.filter(offer__id=self.id)
        for obj in objs:
            # html += "<p> <a href='%s'>%s</a></p>" %(obj.get_offer_product_url(),obj.product) # this code has been added to show hyperlink tag of offerproducts , but not rendering the html
            list.append('%s' %obj.product)
        return list
    offer_products.allow_html = False
    offer_products.allow_tags = False

    list_display = ('offer_name', 'offer_starts_in', 'offer_ends_in', 'is_approved', '_products', offer_products)

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class OfferProductAdmin(MaterialModelAdmin):
    list_display = ('offer','product','offer_price','offer_product_balance','is_approved')
    list_filter = ('offer','product','is_approved')
    readonly_fields = ["created_by", "modified_by", ]

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


site.register(Offer,OfferAdmin)
site.register(OfferProduct,OfferProductAdmin)