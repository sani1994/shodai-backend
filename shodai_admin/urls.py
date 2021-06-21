from django.urls import path
from shodai_admin import views

urlpatterns = [
    path('login', views.Login.as_view()),
    path('logout', views.Logout.as_view()),
    path('dashboard', views.Dashboard.as_view()),
    path('user/registration', views.AdminUserRegistration.as_view()),
    path('user/profile', views.AdminUserProfile.as_view()),

    # orders
    path('orders', views.OrderList.as_view()),
    path('orders/<int:id>', views.OrderDetail.as_view()),
    path('orders/timeslots', views.TimeSlotList.as_view()),
    path('orders/status', views.OrderStatusList.as_view()),
    path('orders/create', views.CreateOrder.as_view()),
    path('orders/send-notification', views.OrderNotification.as_view()),
    path('orders/status-update', views.OrderStatusUpdate.as_view()),
    path('orders/delivery-zones', views.DeliveryZoneList.as_view()),
    path('orders/platforms', views.PlatformList.as_view()),

    # invoices
    path('invoices/download/pdf/<int:id>', views.InvoiceDownloadPDF.as_view()),

    # customers
    path('customers/search', views.CustomerSearch.as_view()),

    # products
    path('products/search', views.ProductSearch.as_view()),
    path('products/subcategories', views.ProductMetaList.as_view()),

    # offers
    path('offers/delivery-charge', views.DeliveryChargeOfferList.as_view()),

    # coupons
    path('coupons/verify-coupon', views.VerifyCoupon.as_view()),

    # users
    path('users', views.UserList.as_view()),
    path('users/<int:id>', views.UserDetail.as_view()),
    path('users/reset-password', views.UserResetPassword.as_view()),

    # reports
    path('reports/all-customers/download/excel', views.UserListDownloadExcel.as_view()),
    path('reports/order-products/download/excel', views.OrderProductListExcel.as_view()),

    # pre-orders
    path('pre-orders', views.PreOrderList.as_view()),
    path('pre-orders/<int:id>', views.PreOrderDetail.as_view()),
    path('pre-orders/settings', views.PreOrderSettingList.as_view()),
    path('pre-orders/settings/<int:id>', views.PreOrderSettingDetail.as_view()),
    path('pre-orders/process', views.ProcessPreOrder.as_view()),
    path('pre-orders/status', views.PreOrderStatusList.as_view()),
    path('pre-orders/settings/active', views.PreOrderSettingActiveList.as_view()),

    # producers
    path('producers/products/search', views.ProducerProductSearch.as_view()),
]
