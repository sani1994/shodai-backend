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
site.main_bg_color = '#088A3F'
site.main_hover_color = 'black'

# site.profile_picture = staticfiles('../media/shodai.jpg')
site.profile_picture = "https://lh3.googleusercontent.com/hJ504D-hcWebdHJw1WhKixKaC1rj4JL31mB5l1vSX6Tmj6IV7lIRv5rUy-2PWKe4hUzTJazSkCPByyfMaBR9nPJMdmsrJYxa1BOzyvgVguZLWu0mjsnLciAv365wCjyOXW-xyUpLMUZJv9iZUZbtzNool0pcYYyWIVbPQsGsAn4NPfwgEjy7d6_YInJbErp1zzrrP4PgPyr2fDX4rivZBjM2w9nzAxakPb-xJK_s2bTWzkymvLcUsBWL3bByUqdz6MtLFTmR9o-IL56iG0QuCWLJpwdXEu4qwKSfwA2DGc1NF_WDvrSKIgBau6BkZOYbxCd4EICGGfsLpCSf6JOMAohNuY4eupnU4gf4bP8c9cQVYMWyPKfisgFzCN-BUOw1j-loBSP9DbCpCCkUFJcpsvGE_MgxctToORee8CB9576HOceHy0NB_sD0Xbw-O9WTePTf4MwsOzhyUGKDg3KK8001PmSDkNLqwHNDMdKBJ9Xl_jByHFqh_8h-TA8rjrFATsGfwVpfoRDAw6MnDAP40n-XN6_5E4DgT6GodYoUZigjJPp806YiejPU6Vim5SYQpPUF0PBA74Nwp1Ji1F9pC1yEw4Yn07QkI1anv0Mha-TpipLUHTWu9UkeCePp3CCJxLlPiHEJnHKiCaa2pf3aSa_L4olN55J38yR4BVGmE6acjGNU_JTNpFN5e3sp_A=w795-h789-no"


site.profile_bg = "https://lh3.googleusercontent.com/9RyrRW867Rtm-g9uJELf0NwsXLBdugHZOc4T8YsBK5fT81nQzvfOwJF0cpigXJ5q_RJHRcmF0Xs86uab1fohaIa_pyNfL7XeiYL55Gc182nHyP4tmgxUej_LHD6f8h3VZTOWlgFuO_Lgb-742m0478tu2qQHm2zV2HqBOmQCBtIWJFXU8aNCvesDrPncPOboYKEm9tMWf2gyxyGhTOPde7SfxV4eKHvkQNujQhj5rdUELhHyZQy9I4QBqFI3LSZARdSThjSYOsm6brrHP043Ok1uIAqs0fj2a-06mi3Y7hCK1tEMfPvKf1ppaq-nyhejcYkePjbBugY7SFuHN3lzLbB7sgp6G6iyIYnNz47mG1jomlSBWScP4aYLlIatNGEo_1UfZreVgpioGStCoJ6TUzuHoH2fyRYvt5i0-MxS4-5fyqs_eWtmu63npELXpn8r8LMprlZFSfdO087bIhWixuojt758FP0fzMfTn1uMRImBI0-dGC4VrLXWceRwErvG4_18t_EZAVhbVVBa2DjERMazOQDaX_2YQm55ez3_WwdkhEqDd2KPKtanVDAqBHqALGJzFckr4iaDD9JOum0rJx1qlLvQfejSAOwnzWFZmApC7ZI_1Lt2T5yqFVFsx2IjiDt2qMJ-vHkAQ733Dl2jAXErJzzebeJ4PyU9mUE_s6o3_-WA7IvkzBzEM7VZGw=w1019-h789-no"
# site.profile_bg = staticfiles('../media/white.jpg')

# site.login_logo = staticfiles('../media/shodai.jpg')
site.login_logo = "https://lh3.googleusercontent.com/hJ504D-hcWebdHJw1WhKixKaC1rj4JL31mB5l1vSX6Tmj6IV7lIRv5rUy-2PWKe4hUzTJazSkCPByyfMaBR9nPJMdmsrJYxa1BOzyvgVguZLWu0mjsnLciAv365wCjyOXW-xyUpLMUZJv9iZUZbtzNool0pcYYyWIVbPQsGsAn4NPfwgEjy7d6_YInJbErp1zzrrP4PgPyr2fDX4rivZBjM2w9nzAxakPb-xJK_s2bTWzkymvLcUsBWL3bByUqdz6MtLFTmR9o-IL56iG0QuCWLJpwdXEu4qwKSfwA2DGc1NF_WDvrSKIgBau6BkZOYbxCd4EICGGfsLpCSf6JOMAohNuY4eupnU4gf4bP8c9cQVYMWyPKfisgFzCN-BUOw1j-loBSP9DbCpCCkUFJcpsvGE_MgxctToORee8CB9576HOceHy0NB_sD0Xbw-O9WTePTf4MwsOzhyUGKDg3KK8001PmSDkNLqwHNDMdKBJ9Xl_jByHFqh_8h-TA8rjrFATsGfwVpfoRDAw6MnDAP40n-XN6_5E4DgT6GodYoUZigjJPp806YiejPU6Vim5SYQpPUF0PBA74Nwp1Ji1F9pC1yEw4Yn07QkI1anv0Mha-TpipLUHTWu9UkeCePp3CCJxLlPiHEJnHKiCaa2pf3aSa_L4olN55J38yR4BVGmE6acjGNU_JTNpFN5e3sp_A=w795-h789-no"

# site.logout_bg = staticfiles('../media/white.jpg')
site.logout_bg = "https://lh3.googleusercontent.com/9RyrRW867Rtm-g9uJELf0NwsXLBdugHZOc4T8YsBK5fT81nQzvfOwJF0cpigXJ5q_RJHRcmF0Xs86uab1fohaIa_pyNfL7XeiYL55Gc182nHyP4tmgxUej_LHD6f8h3VZTOWlgFuO_Lgb-742m0478tu2qQHm2zV2HqBOmQCBtIWJFXU8aNCvesDrPncPOboYKEm9tMWf2gyxyGhTOPde7SfxV4eKHvkQNujQhj5rdUELhHyZQy9I4QBqFI3LSZARdSThjSYOsm6brrHP043Ok1uIAqs0fj2a-06mi3Y7hCK1tEMfPvKf1ppaq-nyhejcYkePjbBugY7SFuHN3lzLbB7sgp6G6iyIYnNz47mG1jomlSBWScP4aYLlIatNGEo_1UfZreVgpioGStCoJ6TUzuHoH2fyRYvt5i0-MxS4-5fyqs_eWtmu63npELXpn8r8LMprlZFSfdO087bIhWixuojt758FP0fzMfTn1uMRImBI0-dGC4VrLXWceRwErvG4_18t_EZAVhbVVBa2DjERMazOQDaX_2YQm55ez3_WwdkhEqDd2KPKtanVDAqBHqALGJzFckr4iaDD9JOum0rJx1qlLvQfejSAOwnzWFZmApC7ZI_1Lt2T5yqFVFsx2IjiDt2qMJ-vHkAQ733Dl2jAXErJzzebeJ4PyU9mUE_s6o3_-WA7IvkzBzEM7VZGw=w1019-h789-no"

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