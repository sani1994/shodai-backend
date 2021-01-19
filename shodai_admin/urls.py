from django.urls import path
from shodai_admin import views

app_name = 'shodai_admin'
urlpatterns = [
    path('login', views.Login.as_view()),
    path('logout', views.Logout.as_view()),
    path('user/registration', views.AdminUserRegistration.as_view()),
    path('user/profile', views.AdminUserProfile.as_view()),

    # orders
    path('orders', views.OrderList.as_view()),
    path('orders/<int:id>', views.OrderDetail.as_view()),
    path('orders/timeslots', views.TimeSlotList.as_view()),
    path('orders/status', views.OrderStatusList.as_view()),
    path('orders/create', views.CreateOrder.as_view()),
    path('orders/send-notification', views.OrderNotification.as_view()),

    # invoices
    path('invoices/download/pdf/<int:id>', views.InvoiceDownloadPDF.as_view()),

    # customers
    path('customers/search', views.CustomerSearch.as_view()),

    # products
    path('products/search', views.ProductSearch.as_view()),
]
