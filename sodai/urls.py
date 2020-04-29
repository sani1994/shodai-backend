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
site.main_bg_color = 'skyblue'
site.main_hover_color = 'black'
site.profile_picture = staticfiles('../media/shodai.jpg')
site.profile_bg = staticfiles('../media/white.jpg')
site.login_logo = staticfiles('../media/shodai.jpg')
site.logout_bg = staticfiles('../media/white.jpg')
site.login_bg_color = 'skyblue'
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