"""shodai URL Configuration

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
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.templatetags.static import static as staticfiles
from django.utils.translation import ugettext_lazy as _
from material.admin.sites import site
from graphene_django.views import GraphQLView
from .schema import schema


# optional
###################################################
site.site_header = _('Shodai')
site.site_title = _('Shodai')
site.main_bg_color = '#088A3F'
site.login_bg_color = '#088A3F'
site.main_hover_color = 'black'

site.favicon = staticfiles('../static/others/favicon.ico')
site.profile_picture = staticfiles('../static/others/shodai-logo.png')
site.profile_bg = staticfiles('../static/others/white.jpg')
site.login_logo = staticfiles('../static/others/shodai-logo.png')
site.logout_bg = staticfiles('../static/others/white.jpg')
##################################################

urlpatterns = [
    path('', include('order.urls')),
    path('', include('customer_service.urls')),
    path('', include('product.urls')),
    path('', include('producer.urls')),
    path('', include('retailer.urls')),
    path('', include('userProfile.urls')),
    path('', include('offer.urls')),
    path('', include('coupon.urls')),
    path('', include('utility.urls')),
    # path('', include('search.urls')),
    path('admins/', include('shodai_admin.urls')),
    path('admin/', include('material.admin.urls')),
    path('notifications/', include(notifications.urls, namespace='notifications')),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # Landing
    url(r'^$', TemplateView.as_view(template_name='landing/index.html')),
    url(r'^download/app', TemplateView.as_view(template_name='landing/download.html')),

    # Graphql
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
