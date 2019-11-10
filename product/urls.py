from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from product import views
# import views

urlpatterns = [
    path('product/', views.ProductList.as_view()),
    path('product/<int:id>/', views.ProductDetail.as_view()),
    path('productcatagory/', views.ProductCategoryList.as_view()), # get post product catagory
    path('productcatagory/<int:id>/', views.ProductCategoryDetail.as_view()),  # update and delete product catagory
    path('productcategorydetails/<int:id>/',views.ProductCategoryDetails.as_view()), #post productCategory id and get list of productMeta
    path('shopcatagory/', views.ShopCategoryList.as_view()), #get post shop catagory
    path('shopcatagory/<int:id>/', views.ShopCategoryDetail.as_view()), # update and delete shop catagory
    path('productmeta/',views.ProductMetaList.as_view()),
    path('productmeta/<int:id>/',views.ProductMetaDetail.as_view()),
    path('productmetadetails/<int:id>/',views.ProductMetaDetails.as_view()), #post productMeta id and get list of product
    path('productunit/',views.ProductUnitList.as_view()),#post product_unit get product_unit list
    path('productunit/<int:id>/',views.ProductUnitList.as_view())# update and delete product_unit
]

urlpatterns = format_suffix_patterns(urlpatterns)