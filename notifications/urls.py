from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='manage'),
	url(r'^category/(?P<slug>[\w_-]+)/$', views.IndexView.as_view(), name='manage_cat'),
	url(r'^set_goal/$', views.set_goal, name='set_goal'),
	url(r'^ajax/(?P<id>[\w_-]+)/$', views.AjaxNotifications.as_view(), name='ajax_view'),
	url(r'^ajax_history/(?P<id>[\w_-]+)/$', views.AjaxHistory.as_view(), name='ajax_history'),
	url(r'^(?P<slug>[\w_-]+)/$', views.SubjectNotifications.as_view(), name='view'),
	url(r'^(?P<slug>[\w_-]+)/history/$', views.SubjectHistory.as_view(), name='history'),
]