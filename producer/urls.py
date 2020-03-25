from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from producer import views

urlpatterns = [
    path('producerproduct/', views.PeroducerBulkRequestList.as_view()),
    path('producerproduct/<int:id>/', views.PeroducerBulkRequestDetails.as_view()),
    path('producerbusinesstype/',views.BusinessTypeList.as_view()),
    path('producerbusinesstype/<int:id>/', views.BusinessTypeDetails.as_view()),
    path('producerbusiness/',views.ProducerBusinessList.as_view()),
    path('producerbusiness/<int:id>/',views.ProducerBusinessDetails.as_view()),
    path('producerfarm/', views.ProducerFarmList.as_view()),
    path('producerfarm/<int:id>/', views.ProducerFarmDetail.as_view()),
    path('productlistforcustomer/',views.ProducerProductListForCustomer.as_view()),
    path('bulkorder/',views.BulkOrderList.as_view()),
    path('bulkorder/<int:id>/',views.BulkOrderDetails.as_view()),
    path('bulkorderproducts/',views.BulkOrderProductsList.as_view()),
    path('bulkorderproducts/<int:id>/', views.BulkOrderProductsDetails.as_view()),
    path('microbulkorder/',views.MicroBulkOrderList.as_view()),
    path('microbulkorder/<int:id>/', views.MicroBulkOrderDetails.as_view()),
    path('microbulkorderproducts/', views.MicroBulkOrderProductsList.as_view()),
    path('microbulkorderproducts/<int:id>/', views.MicroBulkOrderProductsDetails.as_view()),
    path('sharable-code-accept/', views.SharableCodeAccept.as_view()), # return bulk_order_product object by taking sharable code
]

urlpatterns = format_suffix_patterns(urlpatterns)