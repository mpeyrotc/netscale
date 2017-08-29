"""netscale URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import mainApp.views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', mainApp.views.home, name='home'),
    url(r'^netscale/login$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
    url(r'^registration$', mainApp.views.registration, name='registration'),
    url(r'^add-email$', mainApp.views.add_email, name='add_email'),
    url(r'^add-contacts$', mainApp.views.add_contacts, name='add_contacts'),
    url(r'^profiles/(?P<id>\d+)$', mainApp.views.profiles, name='profiles'),
    url(r'^friendship/', include('friendship.urls')),
    url(r'^sendRequest/(?P<other_id>\d+)/(?P<user_id>\d+)$', mainApp.views.send_request, name='send_request'),
    url(r'^acceptRequest/(?P<req_id>\d+)$', mainApp.views.accept_request, name='accept_request'),
    url(r'^rejectRequest/(?P<req_id>\d+)$', mainApp.views.reject_request, name='reject_request'),
    url(r'^network$', mainApp.views.network, name='network'),
    url(r'^edit_profile$', mainApp.views.edit_profile, name='edit_profile'),
    url(r'^netscale-friends$', mainApp.views.netscale_friends, name='netscale_friends'),
    url(r'^data2$', mainApp.views.data2, name='data2')
]
