from django.conf import settings
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from userProfile import views
from rest_framework_simplejwt import views as jwt_views
from django.conf.urls.static import static

urlpatterns = [
    path('refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('userprofile/', views.UserProfileList.as_view()),
    path('userprofiledetails/<int:id>/', views.UserProfileDetail.as_view()),
    path('address/', views.AddressList.as_view()),
    path('address/<int:id>/', views.AddressDetail.as_view()),
    path('login/',views.Login.as_view()),
    path('logout/',views.Logout.as_view()),
    path('userregistration/',views.UserRegistration.as_view()), #registration for normal user
    path('otp/',views.OtpCode.as_view()),
    path('otpverify/',views.OtpVerify.as_view()),
    path('retailerregistration/',views.RetailerRegistration.as_view()), #registration for retailer
    path('producerregistration/',views.RetailerRegistration.as_view()) ,#producer registration.. same as retailer so that used same view
    path('', views.Home.as_view()),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns = format_suffix_patterns(urlpatterns)