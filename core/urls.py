from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
	url(r'^login/$', views.login, name='home'),
	url(r'^register/$', views.RegisterUser.as_view(), name='register'),
	url(r'^remember_password/$', views.remember_password, name='remember_password'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'core:home'}, name='logout'),
]
