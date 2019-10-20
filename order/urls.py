from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from order import views

urlpatterns = [
    path('order/', views.OrderList.as_view()),
    path('order/<int:id>/', views.OrderDetail.as_view()),
    path('orderdetails/<int:id>/',views.OrderDeatils.as_view()), # give order id and get all the products related to the order
    path('orderproduct/',views.OrderProductList.as_view()),
    path('orderproduct/<int:id>/',views.OrderProductDetail.as_view()),
    path('vat/', views.VatList.as_view()),
    path('vat/<int:id>/',views.VatDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)