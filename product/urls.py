from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from product import views
# import views

urlpatterns = [
    path('product/', views.ProductList.as_view()),
    path('productdetail/<int:pk>/', views.ProductDetail.as_view()),
    path('productcatagory/', views.ProductCategoryList.as_view()), # get post product catagory
    path('productcatagorydetails/<int:pk>', views.ProductCategoryDetail.as_view()),  # update and delete product catagory
    path('shopcatagory/', views.ShopCategoryList.as_view()), #get post shop catagory
    path('shopcatagorydetails/<int:pk>', views.ShopCategoryDetail.as_view()), # update and delete shop catagory
    path('productmetalist/',views.ProductMetaList.as_view()),
    path('productmetadetail/<int:pk>',views.ProductMetaDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)