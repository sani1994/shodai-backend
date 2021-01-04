from django.urls import path
from shodai_admin import views
from rest_framework_simplejwt import views as jwt_views

app_name = 'shodai_admin'
urlpatterns = [
    path('refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),

    path('login/', views.AdminLogin.as_view()),
    path('logout/', views.Logout.as_view()),
    path('profile/<int:id>/', views.AdminProfileDetail.as_view()),

    # orders
    path('orders', views.OrderList.as_view()),
    path('orders/<int:id>', views.OrderDetail.as_view()),
    path('orders/timeslots', views.TimeSlotList.as_view()),
    path('orders/status', views.OrderStatusList.as_view()),

    # products
    path('products/search', views.ProductSearch.as_view()),

    # REST_FRAMEWORK Token Authentication Test API
    path('login-test/', views.LoginTest.as_view()),
    path('logout-test/', views.LogoutTest.as_view()),
    path('token-view-test/', views.TokenViewAPITest.as_view()),
]
