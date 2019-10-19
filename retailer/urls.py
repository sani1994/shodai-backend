from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from retailer import views

urlpatterns = [
    # path('retailer/', views.RetailerList.as_view()),
    # path('retailer/<int:pk>/', views.RetailerDetail.as_view()),
    path('shop/', views.ShopList.as_view()),
    path('shop/<int:id>/',views.ShopDetail.as_view()),
    path('account/',views.AccountList.as_view()),
    path('account/<int:id>/',views.AccountDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)