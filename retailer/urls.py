from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from retailer import views

urlpatterns = [
    # path('retailer/', views.RetailerList.as_view()),
    # path('retailer/<int:pk>/', views.RetailerDetail.as_view()),
    path('shop/', views.ShopList.as_view()),
    path('shop/<int:id>/',views.ShopDetail.as_view()),
    path('account/',views.AccountList.as_view()),
    path('account/<int:id>/',views.AccountDetail.as_view()),
    path('acceptorder/',views.AcceptedOrderList.as_view()), #to accept order with order id
    path('acceptedorderdetail/<int:id>/', views.AcceptedOrderDetail.as_view()), #get accepted order detail and delete only
    path('getshoplist/<int:id>/',views.RetailerShopList.as_view()), #give user id(retailer id) get retailer shop list for that retailer or user
    # path('updateorderstatus/<int:id>/',views.OrderStatusUpdate.as_view()) # give acceptorder id and order_status order of the accepted order will update to the given update
    path('shopproduct/', views.ShopProductList.as_view(),name = 'shopproduct-list'), #get list and add shop product
    path('shopproduct/<int:id>/', views.ShopPeroductDetail.as_view(), name='shopproduct-detail') ,#get , update and delete shopproduct
    path('hasshop/', views.HasShop.as_view(),name = 'hasshop-boolean'), # return boolean value on a user has shop or not
    path('shopproductsforcustomer/',views.ShopProductForCustomer.as_view(),name = 'shopproductforcutsomer-list'), #get nearby shop products
    path('nearbyshops/', views.GetNearbyShops.as_view(), name = 'nearbyshops-list'), #get nearby shops
    path('getshopproducts/<int:id>/', views.GetNearbyShopProducts.as_view(), name = 'nearbyshoproduct-list'), #get shop products by shop id

]

urlpatterns = format_suffix_patterns(urlpatterns)