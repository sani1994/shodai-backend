from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from order import views

urlpatterns = [
    path('order/', views.OrderList.as_view()), #get and post request
    path('order/<int:id>/', views.OrderDetail.as_view()), # get,put,delete request for a single object
    path('orderproductlist/<int:id>/',views.OrderdProducts.as_view()), # give order id and get all the products related to the order
    path('orderproduct/',views.OrderProductList.as_view()), #get and post request
    path('orderproduct/<int:id>/',views.OrderProductDetail.as_view()), # get,put,delete request for a single object
    path('vat/', views.VatList.as_view()), #get and post request
    path('vat/<int:id>/',views.VatDetail.as_view()), # get,put,delete request for a single object
    path('updateorderstatus/<int:id>/',views.OrderStatusUpdate.as_view()) # give acceptorder id and order_status order of the accepted order will update to the given order status
]
urlpatterns = format_suffix_patterns(urlpatterns)