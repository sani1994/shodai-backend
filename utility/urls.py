from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from utility import views

urlpatterns = [
    path('area/', views.AreaList.as_view()),
    path('area/<int:id>/', views.AreaDetails.as_view()),
    path('remarks/',views.RemarksList.as_view()),
    path('remarks/',views.RemarksDetails.as_view()),
    path('productunit/',views.ProductUnitList.as_view()),#post product_unit get product_unit list
    path('productunit/<int:id>/',views.ProductUnitList.as_view())# update and delete product_unit
]
urlpatterns = format_suffix_patterns(urlpatterns)