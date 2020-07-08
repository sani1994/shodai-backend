from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from customerService import views

urlpatterns = [
    path('customerQuery/', views.CustomerQueryList.as_view()),
]

