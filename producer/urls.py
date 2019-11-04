from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from producer import views

urlpatterns = [
    path('producerproduct/', views.ProducerProductList.as_view()),
    path('producerproduct/<int:id>/', views.ProducerProductDetail.as_view()),
    path('producerbusinesstype/',views.BusinessTypeList.as_view()),
    path('producerbusinesstype/<int:id>', views.BusinessTypeDetails.as_view()),
    path('producerbusiness/',views.ProducerBusinessList.as_view()),
    path('producerbusiness/<int:id>/',views.ProducerBusinessDetails.as_view()),
    path('producerfarm/', views.ProducerFarmList.as_view()),
    path('producerfarm/<int:id>/', views.ProducerFarmDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)