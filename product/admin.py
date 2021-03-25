import csv
import pandas as pd
import numpy as np

from builtins import super
from django.contrib import admin, messages
from django import forms
from django.shortcuts import redirect, render
from django.urls import path
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from django.http import HttpResponse, HttpResponseRedirect
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from product.models import ShopCategory, ProductCategory, ProductMeta, Product, Manufacturer
from retailer.models import Shop


class FileImportForm(forms.Form):
    uploaded_file = forms.FileField()


class SelectShopForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    shop = forms.ModelChoiceField(Shop.objects)
    # shop = forms.ModelMultipleChoiceField(Shop.objects, widget=forms.CheckboxSelectMultiple)
    # shop_name = forms.ChoiceField(label='Select a Shop', choices=SHOP_CHOICES,
    #                               widget=forms.CheckboxSelectMultiple())


class ProductAdmin(MaterialModelAdmin):
    list_filter = ('product_meta__product_category', 'product_meta', 'product_name', 'is_approved',)
    list_display = ('id', 'product_name', 'product_price', 'price_with_vat', 'is_approved')
    readonly_fields = ["created_by", "modified_by", "created_on", "modified_on",
                       'price_with_vat', 'slug']
    search_fields = ['product_name']
    autocomplete_fields = ('product_unit', 'product_meta',)
    actions = ["save_selected", "export_as_csv", "export_all_as_csv", ]
    fieldsets = (
        ('Product Detail View', {
            'fields': (
                'product_name', 'product_name_bn', 'product_image', 'product_description',
                'product_description_bn', 'product_price', 'product_price_bn', 'product_unit',
                'product_meta', 'product_last_price', 'is_approved', 'decimal_allowed', 'price_with_vat',
                'created_by', 'modified_by', 'created_on', 'modified_on')
        }),
    )

    def get_actions(self, request):
        actions = super(ProductAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            return []
        else:
            return actions

    def save_selected(self, request, queryset):
        for obj in queryset:
            obj.save()

    save_selected.short_description = "Save Selected"

    def export_as_csv(self, request, queryset):
        field_names = ['id', 'product_name', 'product_name_bn', 'product_unit', 'product_price', 'product_last_price',
                       'price_with_vat', 'product_category_name', 'product_meta', 'is_approved', 'product_image']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=product.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = "Export Selected"

    def export_all_as_csv(self, request, queryset):
        field_names = ['id', 'product_name', 'product_name_bn', 'product_unit', 'product_price',
                       'product_last_price', 'price_with_vat', 'product_meta', 'is_approved', 'product_image']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=all_product.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        all_product = Product.objects.all()
        for obj in all_product:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_all_as_csv.short_description = "Export All"

    change_list_template = "product/product_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-file/', self.import_file),
        ]
        return my_urls + urls

    def export_to_shop_product(self, request, queryset):
        form = SelectShopForm(request.POST)
        if request.POST.get('apply') == 'Copy Product':
            if form.is_valid():
                shop = form.cleaned_data['shop']
                print(shop)
                messages.success(request, 'shops were updated')
                return HttpResponseRedirect(request.get_full_path())

        return render(request, 'product/shop_product.html',
                      {'objects': queryset,
                       'form': form})

    export_to_shop_product.short_description = "Export Selected Products to Shop"

    def import_file(self, request):
        if not request.user.is_superuser:
            messages.success(request, "You are not authorised for this action")
            return redirect("..")
        else:
            if request.method == "POST":
                content_type = request.FILES['uploaded_file'].content_type
                if content_type == 'text/csv':
                    data = pd.read_csv(request.FILES["uploaded_file"])
                elif (content_type == 'application/vnd.ms-excel' or
                      content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
                    data = pd.read_excel(request.FILES["uploaded_file"])
                elif (content_type == 'application/vnd.oasis.opendocument.spreadsheet' or
                      content_type == 'application/vnd.oasis.opendocument.spreadsheet-template'):
                    data = pd.read_excel(request.FILES["uploaded_file"], engine="odf")
                else:
                    messages.success(request, 'File format not supported.')
                    return redirect("..")

                length = len(data.index)
                count = 0
                for i in range(length):
                    if (not pd.isna(data["id"][i]) and
                            not pd.isna(data["product_price"][i]) and not pd.isna(data["is_approved"][i])):
                        product = Product.objects.filter(id=data["id"][i])
                        if product:
                            product = product[0]
                            flag = False
                            if isinstance(data["product_price"][i],
                                          (np.int64, np.float32)) and product.product_price != float(
                                data["product_price"][i]):
                                product.product_last_price = product.product_price
                                product.product_price = float(data["product_price"][i])
                                flag = True
                            if isinstance(data["is_approved"][i], np.bool_) and product.is_approved != \
                                    data["is_approved"][i]:
                                product.is_approved = data["is_approved"][i]
                                flag = True
                            if flag:
                                product.save()
                                count += 1
                        else:
                            print("Product ID {} does not exists in database".format(data["id"][i]))
                            # message = "row " + str(i) + " in your csv failed because product does not exist"
                            # messages.success(request, message)
                    else:
                        print("Required information is empty in row {}".format(i + 1))
                        # message = "row " + str(i) + " in your csv failed because of empty value"
                        # messages.success(request, message)

                messages.success(request, 'Successful: {}, Ignored: {}'.format(count, length - count))
                return redirect("..")
            form = FileImportForm()
            payload = {"form": form}
            return render(
                request, "product/csv_form.html", payload
            )

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


class ProductUnitAdmin(ImportExportModelAdmin):
    list_display = ('product_unit', 'history')

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()


class ShopCategoryResource(resources.ModelResource):
    class Meta:
        model = ShopCategory
        fields = ('id', 'type_of_shop')


class ShopCategoryAdmin(ImportExportModelAdmin):
    list_display = ('type_of_shop', 'created_by')
    readonly_fields = ["created_by", "modified_by", ]
    resource_class = ShopCategoryResource

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


class ProductCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "modified_by", ]
    list_display = ("type_of_product",)

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


class ProductMetaAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "modified_by", ]
    list_display = ('id', 'name', 'product_category', 'shop_category', 'vat_amount')
    list_filter = ('product_category', 'shop_category')
    search_fields = ['name']

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


# class ManufacturerAdmin(admin.ModelAdmin):
#     readonly_fields = ["created_by", "modified_by", "created_on", "modified_on", "code"]
#     list_display = ('id', 'name', 'code', 'is_approved')
#
#     def save_model(self, request, obj, form, change):
#         if obj.id:
#             obj.modified_by = request.user
#         else:
#             obj.created_by = request.user
#         obj.save()
#
#     def has_delete_permission(self, request, obj=None):
#         return False


site.register(Product, ProductAdmin)
site.register(ShopCategory, ShopCategoryAdmin)
site.register(ProductCategory, ProductCategoryAdmin)
site.register(ProductMeta, ProductMetaAdmin)
# site.register(Manufacturer, ManufacturerAdmin)
# site.register(ProductUnit, ProductUnitAdmin)
