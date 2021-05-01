from django.contrib import admin, messages
from django.forms import forms
from leaflet.admin import LeafletGeoAdminMixin
from rest_framework.generics import get_object_or_404

from user.models import UserProfile
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from retailer.models import Account, Shop, ShopProduct, AcceptedOrder


# Register your models here.
#
# class UserInline(admin.StackedInline):
#     """ Details a person in line. """
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'person'
#
#     fields = ('email', 'first_name', 'last_name', 'city')
#
#
# class RetailerAdmin(admin.ModelAdmin):
#     list_display = ('user_id', 'user', 'address', 'retailer_email', 'retailer_website')
#     exclude = ['created_by', 'modified_by']
#     # inlines = [
#     #     UserInline
#     # ]
#
#     def save_model(self, request, obj, form, change):
#         print(obj.pk)
#         if obj.pk == None:
#             print("inside None")
#             obj.created_by = request.user
#             obj.modified_by = request.user
#         super().save_model(request,obj, form, change)

# admin.site.unregister(Retailer)
#
#
#
# admin.site.register(Retailer, RetailerAdmin)
# admin.site.register(RetailerAdmin)

class ShopProductInline(admin.StackedInline):
    model = ShopProduct
    fields = ['product', 'product_stock', 'product_price', 'product_unit', ]
    readonly_fields = ['product_unit']
    autocomplete_fields = ('product',)

    def get_queryset(self, request):
        qs = super(ShopProductInline, self).get_queryset(request)
        return qs.filter(is_approved=True)


class ShopAdmin(LeafletGeoAdminMixin, MaterialModelAdmin):
    model = Shop
    list_display = ('shop_name', 'is_approved')
    readonly_fields = ["created_by", "modified_by", 'user', 'created_on', 'modified_on']
    verbose_name = 'Shop'
    inlines = [ShopProductInline, ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        if instances:
            for instance in instances:
                if ShopProduct.objects.filter(product=instance.product, shop=instance.shop).exists():
                    messages.success(request, 'Item already Exists in the shop')
                else:
                    instance.is_approved = True
                    instance.product_unit = instance.product.product_unit
                    instance.product_last_price = instance.product.product_last_price
                    instance.created_by = request.user
                    instance.save()
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
            obj.save()
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class AcceptedOrderAdmin(MaterialModelAdmin):
    model = AcceptedOrder
    list_display = ('order', 'user')
    readonly_fields = ["created_by", "modified_by", 'user', 'order', 'order_product']


class ShopProductAdmin(MaterialModelAdmin):
    model = ShopProduct
    list_display = ('product', 'shop', 'product_stock')
    readonly_fields = ["created_by", "modified_by", 'product_last_price', 'created_on', 'modified_on']
    search_fields = ['shop__shop_name', 'product__product_name', ]
    list_filter = ('shop__shop_area',)

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
            old_obj = get_object_or_404(ShopProduct, id=obj.id)
            obj.product_last_price = old_obj.product_price
            obj.save()
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


site.register(Shop, ShopAdmin)
site.register(Account)
site.register(AcceptedOrder, AcceptedOrderAdmin)
site.register(ShopProduct, ShopProductAdmin)
