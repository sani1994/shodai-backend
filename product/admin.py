import csv
import pandas as pd
from builtins import super

from django.contrib import admin, messages
from django.forms import forms
from django import forms
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.text import slugify
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from rest_framework.generics import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from product.models import ShopCategory, ProductCategory, ProductMeta, Product
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from retailer.models import Shop
from utility.models import ProductUnit


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class SelectShopForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    shop = forms.ModelChoiceField(Shop.objects)
    # shop_name = forms.ChoiceField(label='Select a Shop', choices=SHOP_CHOICES,
    #                               widget=forms.CheckboxSelectMultiple())


class ProductAdmin(MaterialModelAdmin):
    list_filter = ('product_meta__product_category', 'product_meta', 'product_name', 'is_approved',)
    list_display = ('id', 'product_name', 'product_price', 'price_with_vat', 'is_approved')
    readonly_fields = ["created_by", "modified_by", 'price_with_vat', 'slug']
    search_fields = ['product_name']
    autocomplete_fields = ('product_unit',)
    actions = ["save_selected", "export_as_csv", "export_all_as_csv", "export_to_shop_product"]

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
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def export_to_shop_product(self, request, queryset):
        if 'apply' in request.POST:
            form = SelectShopForm(request.POST)
            if form.is_valid():
                shop = form.cleaned_data['shop']
                print(shop)
                messages.success(request, 'shops were updated')
                return HttpResponseRedirect(request.get_full_path())

        form = SelectShopForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        return render(request, 'product/shop_product.html',
                      {'objects': queryset,
                       'form': form})

    export_to_shop_product.short_description = "Export Selected Products to Shop"

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            data = pd.read_csv(csv_file)
            length = len(data.index)
            # Create objects from passed in data
            for i in range(length):
                if not pd.isna(data["product_name"][i]) and not pd.isna(data["product_unit"][i]):
                    slug = slugify(data["product_name"][i] + "-" + data["product_unit"][i])
                    print(slug)
                    if Product.objects.filter(slug=slug).exists():
                        product = Product.objects.get(slug=slug)
                        product.product_price = float(data["product_price"][i]) if not pd.isna(data["product_price"][i]) else product.product_price
                        print(product.product_price)
                        product.is_approved = data["is_approved"][i] if not pd.isna(data["is_approved"][i]) else product.is_approved
                        product.save()
                        self.message_user(request, "Your csv file has been imported")
                    else:
                        print("Product does not exists in database")
                        message = "row" + str(i) + "in your csv failed because product does not exist"
                        self.message_user(request, message)
                else:
                    print("Product name or unit is Nan")
                    message = "row" + str(i) + "in your csv failed because of empty value"
                    self.message_user(request, message)
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "product/csv_form.html", payload
        )

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
            old_obj = get_object_or_404(Product, id=obj.id)
            # obj.product_last_price = old_obj.product_price
            obj.save()
        else:
            obj.created_by = request.user
            obj.save()
        return super().save_model(request, obj, form, change)


class ProductUnitAdmin(ImportExportModelAdmin):
    list_display = ('product_unit', 'history')

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


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
        return super().save_model(request, obj, form, change)


class ProductCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "modified_by", ]
    list_display = ("type_of_product",)

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


class ProductMetaAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "modified_by", ]
    list_display = ('id', 'name', 'product_category', 'shop_category', 'vat_amount')
    list_filter = ('product_category', 'shop_category')

    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        obj.save()
        return super().save_model(request, obj, form, change)


site.register(Product, ProductAdmin)
site.register(ShopCategory, ShopCategoryAdmin)
site.register(ProductCategory, ProductCategoryAdmin)
site.register(ProductMeta, ProductMetaAdmin)
# site.register(ProductUnit, ProductUnitAdmin)
