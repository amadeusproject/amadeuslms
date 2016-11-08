from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import password_reset, password_reset_done,password_reset_confirm, password_reset_complete
from . import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'logs', views.LogViewSet)
urlpatterns = [
	url(r'^$', views.login, name='home'),
	url(r'^register/$', views.RegisterUser.as_view(), name='register'),
	url(r'^remember_password/$', views.remember_password, name='remember_password'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'core:home'}, name='logout'),
    url(r'^notification/([0-9]+)/$', views.processNotification, name='notification_read'),
    url(r'^getNotifications/$', views.getNotifications, name='getNotifications'),
    url(r'^guest/$', views.GuestView.as_view(), name='guest'),

    #API REST
    url(r'^', include(router.urls)),
    #url(r'^logs/$', views.get_log),

#Reset Password

	url(r'^reset/$', password_reset, {'template_name':'registration/passwor_reset_form.html',
									'email_template_name':'registration/passwor_reset_email.html',
									'subject_template_name' :'registration/password_reset_subject.txt',
									'post_reset_redirect':'done/'}, name="password_reset"),
	url(r'^reset/done/$', password_reset_done, {'template_name':'registration/passwor_reset_done.html'}),
	url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$', password_reset_confirm,
									{'template_name':'registration/passwor_reset_confirm.html',
									'post_reset_redirect' : '/done/'},
									name='password_reset_confirm'),
	url(r'^done/$', password_reset_complete,{'template_name':'registration/passwor_reset_complete.html'}),

]


