import csv
import pandas as pd
from builtins import super

from django.contrib import admin
from django.forms import forms
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.text import slugify
from material.admin.options import MaterialModelAdmin
from material.admin.sites import site
from rest_framework.generics import get_object_or_404
from django.http import HttpResponse

from product.models import ShopCategory, ProductCategory, ProductMeta, Product
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Register your models here.
from utility.models import ProductUnit


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class ProductAdmin(MaterialModelAdmin):
    list_filter = ('product_name', 'product_meta', 'is_approved')
    list_display = ('id', 'product_name', 'product_price', 'price_with_vat', 'is_approved')
    readonly_fields = ["created_by", "modified_by", 'price_with_vat', 'slug']
    search_fields = ['product_name']
    autocomplete_fields = ('product_unit',)
    actions = ["save_selected", "export_as_csv", "export_all_as_csv"]

    def save_selected(self, request, queryset):
        for obj in queryset:
            obj.save()

    save_selected.short_description = "Save Selected"

    def export_as_csv(self, request, queryset):
        field_names = ['id', 'product_name', 'product_name_bn', 'product_unit', 'product_price',
                       'product_last_price', 'price_with_vat', 'product_meta', 'is_approved', 'product_image']

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

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            data = pd.read_csv(csv_file)
            length = len(data.index)
            # Create objects from passed in data
            for i in range(length):
                slug = slugify(data["product_name"][i] + "-" + data["product_unit"][i])
                if Product.objects.filter(slug=slug).exists():
                    print("Product already exists in database")
                    message = "row" + i + "in your csv failed because of duplicate value"
                    self.message_user(request, message)
                else:
                    Product.objects.create(product_name=data["product_name"][i],
                                           product_image=data["product_image"][i],
                                           product_description=data["product_description"][i],
                                           product_description_bn=data["product_description_bn"][i],
                                           product_price=data["product_price"][i],
                                           product_last_price=data["product_last_price"][i],
                                           is_approved=True
                                           )
                    self.message_user(request, "Your csv file has been imported")
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
