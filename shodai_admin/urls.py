from django.conf import settings
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from shodai_admin import views
from rest_framework_simplejwt import views as jwt_views
from django.conf.urls.static import static

app_name = 'shodai_admin'
urlpatterns = [
    path('refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),

    path('login/', views.AdminLogin.as_view()),
    path('logout/', views.Logout.as_view()),
    path('profile/<int:id>/', views.AdminProfileDetail.as_view()),
    path('orders/', views.OrderList.as_view()),

    # REST_FRAMEWORK Token Authentication Test API
    path('login-test/', views.LoginTest.as_view()),
    path('logout-test/', views.LogoutTest.as_view()),
    path('token-view-test/', views.TokenViewAPITest.as_view()),
]
