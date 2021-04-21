from rest_framework.urlpatterns import format_suffix_patterns
from coupon import views
from django.urls import path

urlpatterns = [
    path('verify-coupon/', views.VerifyCoupon.as_view()),
    path('coupon-list/', views.CouponList.as_view()),
    path('referral-coupon/', views.ReferralCoupon.as_view()),
    path('referral-coupon-one/', views.ReferralCouponOne.as_view()),
    path('coupon-page/', views.CouponPage.as_view()),
    path('coupon-count/', views.CouponCount.as_view()),

]
urlpatterns = format_suffix_patterns(urlpatterns)
