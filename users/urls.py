from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^login/$', views.login, name='login'),
	url(r'^logout/$', auth_views.logout, {'next_page': 'users:login'}, name='logout'),
	url(r'^signup/$', views.RegisterUser.as_view(), name = 'signup'),
	url(r'^$', views.UsersListView.as_view(), name = 'manage'),
	url(r'^profile/$', views.Profile.as_view(), name = 'profile'),
	url(r'^edit_profile/$', views.UpdateProfile.as_view(), name = 'edit_profile'),
]
