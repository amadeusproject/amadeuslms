from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w_-]+)/$', views.CreateView.as_view(), name = 'create'),
	url(r'^update/(?P<topic_slug>[\w_-]+)/(?P<slug>[\w_-]+)/$', views.UpdateView.as_view(), name = 'update'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.DeleteView.as_view(), name = 'delete'),
	url(r'^download/(?P<slug>[\w_-]+)/$', views.DownloadFile.as_view(), name = 'download'),
    url(r'^chart/(?P<slug>[\w_-]+)/$', views.StatisticsView.as_view(), name = 'get_chart'),
    url(r'^send-message/(?P<slug>[\w_-]+)/$', views.SendMessage.as_view(), name = 'send_message'),
]
