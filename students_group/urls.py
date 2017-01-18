from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^(?P<slug>[\w_-]+)/$', views.IndexView.as_view(), name='index'),
	url(r'^create/(?P<slug>[\w_-]+)/$', views.CreateView.as_view(), name='create'),
]