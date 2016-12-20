from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^login/$', views.login, name='login'),
	url(r'^logout/$', auth_views.logout, {'next_page': 'users:login'}, name='logout'),
	url(r'^signup/$', views.RegisterUser.as_view(), name = 'signup'),
]
