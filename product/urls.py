from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from product import views
# import views

urlpatterns = [
    path('product/', views.ProductList.as_view()),
    path('product/<int:pk>/', views.ProductDetail.as_view()),
    path('productcatagory/', views.ProductCategoryList.as_view()),
    path('productcatagory/<int:pk>', views.ProductCategoryList.as_view()),
    path('shopcatagory/', views.ShopCategoryList.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)