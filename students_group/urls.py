from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^(?P<slug>[\w_-]+)/$', views.IndexView.as_view(), name='index'),
	url(r'^create/(?P<slug>[\w_-]+)/$', views.CreateView.as_view(), name='create'),
	url(r'^update/(?P<sub_slug>[\w_-]+)/(?P<slug>[\w_-]+)/$', views.UpdateView.as_view(), name='update'),
	url(r'^replicate/(?P<slug>[\w_-]+)/(?P<group_slug>[\w_-]+)/$', views.CreateView.as_view(), name='replicate'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.DeleteView.as_view(), name = 'delete'),
]