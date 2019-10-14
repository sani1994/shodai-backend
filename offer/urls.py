from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from offer import views

urlpatterns = [
    # write urls for offer
    path('offer/', views.OfferList.as_view()),
    path('offer/<int:id>/', views.OfferDetails.as_view())
]
urlpatterns = format_suffix_patterns(urlpatterns)