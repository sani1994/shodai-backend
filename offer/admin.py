from django.contrib import admin
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from offer.models import Offer, OfferProduct, CouponCode, CartOffer


# Register your models here.


class OfferProductInline(admin.StackedInline):
    model = OfferProduct
    fields = ['product', 'offer_price', 'offer_product_balance']
    autocomplete_fields = ('product',)

    def has_delete_permission(self, request, obj=None):
        return False


class CartOfferInline(admin.TabularInline):
    model = CartOffer
    fields = ['updated_delivery_charge', ]

    def has_delete_permission(self, request, obj=None):
        return False


class OfferAdmin(MaterialModelAdmin):
    list_filter = ('offer_name', 'offer_starts_in', 'offer_ends_in', 'is_approved')
    readonly_fields = ["created_on", "created_by", "modified_on", "modified_by"]
    exclude = ['offer_img', 'offer_url']

    def _products(self):
        return OfferProduct.objects.filter(offer__id=self.id).count()

    def offer_products(self):
        list = []
        objs = OfferProduct.objects.filter(offer__id=self.id)
        for obj in objs:
            # html += "<p> <a href='%s'>%s</a></p>" %(obj.get_offer_product_url(),obj.product) # this code has been
            # added to show hyperlink tag of offerproducts , but not rendering the html
            list.append('%s' % obj.product)
        return list

    offer_products.allow_html = False
    offer_products.allow_tags = False

    list_display = ('offer_name', 'offer_starts_in', 'offer_ends_in', 'is_approved', _products, offer_products)
    inlines = (CartOfferInline, OfferProductInline)

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


class OfferProductAdmin(MaterialModelAdmin):
    list_display = ('offer', 'product', 'offer_price', 'offer_product_balance', 'is_approved')
    list_filter = ('offer', 'product', 'is_approved')
    readonly_fields = ["created_by", "modified_by", ]
    search_fields = ['product__product_name']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


class CouponCodeAdmin(MaterialModelAdmin):
    list_display = ('coupon_code', 'created_by')
    readonly_fields = ["created_by", "modified_by", "coupon_code", ]

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class CartOfferAdmin(MaterialModelAdmin):
    list_display = ('offer', 'updated_delivery_charge')
    readonly_fields = ["created_by", "modified_by", "created_on", "modified_on"]
    fieldsets = (
        ('Offer Detail View', {
            'fields': ('offer', 'updated_delivery_charge',
                       'created_by', 'modified_by', 'created_on', 'modified_on')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


site.register(Offer, OfferAdmin)
site.register(OfferProduct, OfferProductAdmin)
site.register(CartOffer, CartOfferAdmin)
# site.register(CouponCode, CouponCodeAdmin)
