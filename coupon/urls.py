from rest_framework.urlpatterns import format_suffix_patterns
from coupon import views
from django.urls import path

urlpatterns = [
    # verify coupon
    path('verify-coupon/', views.VerifyCoupon.as_view()),
    path('coupon-list/', views.CouponList.as_view()),
    path('referral-coupon/', views.ReferralCoupon.as_view()),

]
urlpatterns = format_suffix_patterns(urlpatterns)
