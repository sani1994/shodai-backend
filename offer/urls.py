from rest_framework.urlpatterns import format_suffix_patterns
from offer import views
from django.urls import path

urlpatterns = [
    # write urls for offer
    path('offer/', views.OfferList.as_view()), #get and post request
    path('offer/<int:id>/', views.OfferDetails.as_view()), # get,put,delete request for a single object
    path('offerproduct/', views.OfferProductList.as_view()), ##get and post request
    path('offerproduct/<int:id>/', views.OfferProductDetail.as_view()), # get,put,delete request for a single object
    path('getofferproducts/<int:id>/',views.GetOfferProducts.as_view()) #give offer id and get offer products against that offer
]
urlpatterns = format_suffix_patterns(urlpatterns)
