from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from producer import views

urlpatterns = [
    path('producer/', views.ProducerProductList.as_view()),
    path('producer/<int:pk>/', views.ProducerProductDetail.as_view()),
    path('producer/', views.ProducerFarmList.as_view()),
    path('producer/<int:pk>/', views.ProducerFarmDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)