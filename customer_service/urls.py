from django.urls import path
from customer_service import views

urlpatterns = [
    path('customer-query/', views.CustomerQueryList.as_view()),
]
