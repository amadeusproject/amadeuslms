from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import password_reset, password_reset_done,password_reset_confirm, password_reset_complete
from . import views


urlpatterns = [
	url(r'^$', views.login, name='home'),
	url(r'^register/$', views.RegisterUser.as_view(), name='register'),
	url(r'^remember_password/$', views.remember_password, name='remember_password'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'core:home'}, name='logout'),
    url(r'^notification/([0-9]+)/$', views.processNotification, name='notification_read'),
    url(r'^getNotifications/$', views.getNotifications, name='getNotifications'),
]

#Reset Password
urlpatterns += [
	url(r'^password/reset/$', password_reset, {'post_reset_redirect' : 'password/reset/done/','template_name': 'registration/passwor_reset_form.html'}, name="password_reset"),
	url(r'^password/reset/done/$', password_reset_done, {'template_name': 'registration/passwor_reset_done.html'}),
	url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm, {'post_reset_redirect' : 'password/done/', 'template_name': 'registration/password_reset_confirm.html'}),
	url(r'^password/done/$', password_reset_complete,{'template_name': 'registration/passwor_reset_complete.html'}),

]
