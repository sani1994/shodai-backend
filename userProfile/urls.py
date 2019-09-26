from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from userProfile import views

urlpatterns = [
    path('userprofile/', views.UserProfileList.as_view()),
    path('userprofile/<int:pk>/', views.UserProfileDetail.as_view()),
    path('address/', views.AddressList.as_view()),
    path('address/<int:pk>/', views.AddressDetail.as_view()),
    path('registration/',views.UserRegistration.as_view()),
    path('login/',views.Login.as_view()),
    path('logout/',views.Logout.as_view()),
    path('registration/',views.UserRegistration.as_view()),
    path('otp/',views.OTP.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)