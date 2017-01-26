from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^login/$', views.login, name='login'),
	url(r'^logout/$', views.logout, {'next_page': 'users:login'}, name='logout'),
	url(r'^signup/$', views.RegisterUser.as_view(), name = 'signup'),
	url(r'^forgot_password/$', views.ForgotPassword.as_view(), name = 'forgot_pass'),
	url(r'^reset_password_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.PasswordResetConfirmView.as_view(), name = 'reset_password_confirm'), 
	url(r'^$', views.UsersListView.as_view(), name = 'manage'),
	url(r'^create/$', views.CreateView.as_view(), name = 'create'),
	url(r'^edit/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.UpdateView.as_view(), name = 'update'),
	url(r'^delete/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.DeleteView.as_view(), name = 'delete'),
	url(r'^search/$', views.SearchView.as_view(), name = 'search'),
	url(r'^profile/$', views.Profile.as_view(), name = 'profile'),
	url(r'^edit_profile/$', views.UpdateProfile.as_view(), name = 'edit_profile'),
	url(r'^change_pass/$', views.ChangePassView.as_view(), name='change_pass'),
	url(r'^remove_account/$', views.DeleteView.as_view(), name='remove_acc'),
]
