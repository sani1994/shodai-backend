from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from product import views
# import views

urlpatterns = [
    path('product/', views.ProductList.as_view()),
    path('product/<int:id>/', views.ProductDetail.as_view()),
    path('productcatagory/', views.ProductCategoryList.as_view()), # get post product catagory
    path('productcatagory/<int:id>', views.ProductCategoryDetail.as_view()),  # update and delete product catagory
    path('shopcatagory/', views.ShopCategoryList.as_view()), #get post shop catagory
    path('shopcatagory/<int:id>', views.ShopCategoryDetail.as_view()), # update and delete shop catagory
    path('productmeta/',views.ProductMetaList.as_view()),
    path('productmeta/<int:id>',views.ProductMetaDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)