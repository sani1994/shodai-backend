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
    path('Login/', views.AdminLogin.as_view()),
    path('Logout/', views.Logout.as_view()),
]
