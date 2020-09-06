from django.contrib import admin
from rest_framework.generics import get_object_or_404

from retailer.models import Account, ShopProduct
from userProfile.models import UserProfile
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from retailer.models import Account, Shop, AcceptedOrder


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

class ShopProductInline(admin.TabularInline):
    model = ShopProduct
    fields = ['user', 'product', 'product_stock', ]
    autocomplete_fields = ('user', 'product',)

    def has_delete_permission(self, request, obj=None):
        return False


class ShopAdmin(MaterialModelAdmin):
    model = Shop
    list_display = ('shop_name', 'is_approved')
    readonly_fields = ["created_by", "modified_by", 'user', 'created_on', 'modified_on']
    verbose_name = 'Shop'
    inlines = [ShopProductInline, ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.is_approved = True
            instance.product_unit = instance.product.product_unit
            instance.product_last_price = instance.product.product_last_price
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        # obj.user = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class AcceptedOrderAdmin(MaterialModelAdmin):
    model = AcceptedOrder
    list_display = ('order', 'user')
    readonly_fields = ["created_by", "modified_by", 'user', 'order', 'order_product']


class ShopProductAdmin(MaterialModelAdmin):
    model = ShopProduct
    list_display = ('product', 'shop')
    readonly_fields = ["created_by", "modified_by", 'product_last_price', 'created_on', 'modified_on']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
            old_obj = get_object_or_404(ShopProduct, id=obj.id)
            obj.product_last_price = old_obj.product_price
            obj.save()
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


site.register(Shop, ShopAdmin)
site.register(Account)
site.register(AcceptedOrder, AcceptedOrderAdmin)
site.register(ShopProduct, ShopProductAdmin)
