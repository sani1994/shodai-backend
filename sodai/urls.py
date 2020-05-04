"""sodai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import notifications.urls
from django.contrib import admin
from django.conf import settings
# from django.template.context_processors import static
from django.urls import path, include
from rest_framework import routers
from django.conf.urls.static import static

# from sodai import settings

# for django matreial admin site

from django.contrib.staticfiles.templatetags.staticfiles import static as staticfiles
from django.urls import path, include
from django.utils.translation import ugettext_lazy as _
from material.admin.sites import site

# optional
###################################################
site.site_header = _('Shodai')
site.site_title = _('Shodai')
# site.favicon = staticfiles('../media/')
site.favicon = staticfiles('./static/')
site.main_bg_color = '#088A3F'
site.main_hover_color = 'black'


# site.profile_picture  = staticfiles('./static/userProfile/images/logo.png')
site.profile_picture = staticfiles('../media/shodai.jpg')
# site.profile_picture = "https://lh3.googleusercontent.com/cANBRUuBPtOAV7kZ_YdaD1y3Lvqh94T81gJyDHPg74j-cr5F5b2EysO7VYt7oZIi2y6fYYQEXJNA1IngwQaWElDqgjM6PmTm2vBwLKSh8HKlEB8QBldnOaJky2DdJaFXl5MauPskl1UABOWceON08mENeJqL1T-W4uQH3P6UXsuOMA9fWmwx6DQN6LDQPNzsUKkXFHRIfohG_7GDd5_iIlouJ7wwsZwqG18m6X6dE8g0lVvYp9ORNxY8ol_Ssy-q-ipmFYyZnETaJvCGKvh-J_C8VQqZIxe_oElWggCMzOlal0wNTSdeBgJZ3_bX9duM0TS7jj9FV_Rufaev8XWL8C7mMCAoPxxmjqznXXnJ-rIZYhCX-zcnRoe2qr-8yFTPiZvNjfDUUnS0JTCF25viDw4X5-FYkg1ZYvlUyONSdvBuOuvrym9K2_24YkoXnxoTgoX9Gp9PmGZ2XKITXuGzfsaagX0MDwb-DsA_ddQ_LYenpA-pVQUqI7vijDh83mM63eYwHB9RP7BUIO2kxIbR6Z68c-8WnXXgwVzYUdXuVeYuIOw4KxtFzRqlmPdaAtQ-_LUrxDWfWmHZMhYFxbXz75WrZ5HyZo_ATFZ9-HmAqJdTKRENCehiTsmhVbZFWFfZ5BYjdVcqAlvi_-ZFt95xk0NldY59c55vCKwca3p0bCJREZUP7OvEG_xvzgqy=w910-h903-no"

# site.profile_bg = "https://lh3.googleusercontent.com/WKDzjjFGW5QBhzpihjglOemdJyjv4-XcXZAyHD3Ja0WPGvbsc2nAXiLjKfohjrxWnd0obRviQCIWgzi4r6CH69pW77MfgoxHFXCjkeFJHOmu5X6jYSsDzA-WIW26682vf5x3I_AOYIFWeAqt2TvIycubRoz4KYXu99-vuPiekOT0o-DZM1PUcFCT9-xt0g9GAUMKhFWrZ8LmxBC_t-YXYPCbRkS23Mj33V2IaIsc8jMW52VtZAQRT8jjHvK_DGp_QfqfbY95TF70ISTTW2nDiGgVdPPonSmC4f4bW6a2sje8H_13w8RzH4d9YzooSU5QEIUL-Y_M_pga1OOCwfpENNCIxz7zbrnUnSyxHbZVe1n9TqDxujom_MFgwOM_iqSvpf_FDyG5BIyKC8rlItOMHtoRvuTb2uSMy_a-34A67T4dvGMkmVt_Jqu-o44f_AdoLAQDvTam_F3_72F-E99IYqXalgD7ueciZOGOlm51j67x9-0UQYq04Fmm4CBv5xx3TYKbsaFZfPeMffe_LGw2ArQJkorM9PQ4AHtzpdCedV_0K50zjYesze0a-S8cYfV05uJU2BeHSIbgH-hLf0v5bEZM1GJ0M-DyaIPjyRKm2ZqY1lr38Rc021Z5LsmSg9UYdbim8Nb-PIsD6jVeeS6C5VaMSKhsj8mKdFM1C2aH9M2LFnwifQLHstEVgtVC=w1167-h903-no"
site.profile_bg = staticfiles('../media/white.jpg')

# site.login_logo  = staticfiles('./static/userProfile/images/logo.png')
site.login_logo = staticfiles('../media/shodai.jpg')
# site.login_logo = "https://lh3.googleusercontent.com/cANBRUuBPtOAV7kZ_YdaD1y3Lvqh94T81gJyDHPg74j-cr5F5b2EysO7VYt7oZIi2y6fYYQEXJNA1IngwQaWElDqgjM6PmTm2vBwLKSh8HKlEB8QBldnOaJky2DdJaFXl5MauPskl1UABOWceON08mENeJqL1T-W4uQH3P6UXsuOMA9fWmwx6DQN6LDQPNzsUKkXFHRIfohG_7GDd5_iIlouJ7wwsZwqG18m6X6dE8g0lVvYp9ORNxY8ol_Ssy-q-ipmFYyZnETaJvCGKvh-J_C8VQqZIxe_oElWggCMzOlal0wNTSdeBgJZ3_bX9duM0TS7jj9FV_Rufaev8XWL8C7mMCAoPxxmjqznXXnJ-rIZYhCX-zcnRoe2qr-8yFTPiZvNjfDUUnS0JTCF25viDw4X5-FYkg1ZYvlUyONSdvBuOuvrym9K2_24YkoXnxoTgoX9Gp9PmGZ2XKITXuGzfsaagX0MDwb-DsA_ddQ_LYenpA-pVQUqI7vijDh83mM63eYwHB9RP7BUIO2kxIbR6Z68c-8WnXXgwVzYUdXuVeYuIOw4KxtFzRqlmPdaAtQ-_LUrxDWfWmHZMhYFxbXz75WrZ5HyZo_ATFZ9-HmAqJdTKRENCehiTsmhVbZFWFfZ5BYjdVcqAlvi_-ZFt95xk0NldY59c55vCKwca3p0bCJREZUP7OvEG_xvzgqy=w910-h903-no"


site.logout_bg = staticfiles('../media/white.jpg')
# site.logout_bg = "https://lh3.googleusercontent.com/cANBRUuBPtOAV7kZ_YdaD1y3Lvqh94T81gJyDHPg74j-cr5F5b2EysO7VYt7oZIi2y6fYYQEXJNA1IngwQaWElDqgjM6PmTm2vBwLKSh8HKlEB8QBldnOaJky2DdJaFXl5MauPskl1UABOWceON08mENeJqL1T-W4uQH3P6UXsuOMA9fWmwx6DQN6LDQPNzsUKkXFHRIfohG_7GDd5_iIlouJ7wwsZwqG18m6X6dE8g0lVvYp9ORNxY8ol_Ssy-q-ipmFYyZnETaJvCGKvh-J_C8VQqZIxe_oElWggCMzOlal0wNTSdeBgJZ3_bX9duM0TS7jj9FV_Rufaev8XWL8C7mMCAoPxxmjqznXXnJ-rIZYhCX-zcnRoe2qr-8yFTPiZvNjfDUUnS0JTCF25viDw4X5-FYkg1ZYvlUyONSdvBuOuvrym9K2_24YkoXnxoTgoX9Gp9PmGZ2XKITXuGzfsaagX0MDwb-DsA_ddQ_LYenpA-pVQUqI7vijDh83mM63eYwHB9RP7BUIO2kxIbR6Z68c-8WnXXgwVzYUdXuVeYuIOw4KxtFzRqlmPdaAtQ-_LUrxDWfWmHZMhYFxbXz75WrZ5HyZo_ATFZ9-HmAqJdTKRENCehiTsmhVbZFWFfZ5BYjdVcqAlvi_-ZFt95xk0NldY59c55vCKwca3p0bCJREZUP7OvEG_xvzgqy=w910-h903-no"

site.login_bg_color = '#088A3F'
# site.ordering = ('userProfile','Product')
##################################################

urlpatterns = [
    path('', include('order.urls')),
    path('', include('product.urls')),
    path('', include('producer.urls')),
    path('', include('retailer.urls')),
    path('', include('userProfile.urls')),
    path('', include('offer.urls')),
    path('', include('utility.urls')),
    path('admin/', include('material.admin.urls')),
    path('', include('search.urls')),
    path('notifications/', include(notifications.urls, namespace='notifications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)