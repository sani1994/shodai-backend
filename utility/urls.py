from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from utility import views

urlpatterns = [
    path('area/', views.AreaList.as_view()),
    path('area/<int:id>/', views.AreaDetails.as_view()),
    path('remarks/',views.RemarksList.as_view()),
    path('remarks/',views.RemarksDetails.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)