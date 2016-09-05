from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.CreateUser.as_view(), name='register'),
	url(r'^login/$', auth_views.login, {'template_name': 'index.html'}, name='home'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'home'}, name='logout'),

]
