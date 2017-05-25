from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w_-]+)/$', views.CreateView.as_view(), name = 'create'),
	url(r'^update/(?P<topic_slug>[\w_-]+)/(?P<slug>[\w_-]+)/$', views.UpdateView.as_view(), name = 'update'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.DeleteView.as_view(), name = 'delete'),
	url(r'^window_view/(?P<slug>[\w_-]+)/$', views.NewWindowView.as_view(), name = 'window_view'),
	url(r'^view/(?P<slug>[\w_-]+)/$', views.InsideView.as_view(), name = 'view'),
	url(r'^watch/(?P<ytvideo>[\w_-]+)/$', views.ytvideo_watch_log, name = 'watch'),
	url(r'^finish/(?P<ytvideo>[\w_-]+)/$', views.ytvideo_finish_log, name = 'finish'),
    url(r'^chart/(?P<slug>[\w_-]+)/$', views.StatisticsView.as_view(), name = 'get_chart'),
    url(r'^send-message/(?P<slug>[\w_-]+)/$', views.SendMessage.as_view(), name = 'send_message'),
]
