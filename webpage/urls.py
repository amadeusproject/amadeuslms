from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w_-]+)/$', views.CreateView.as_view(), name = 'create'),
	url(r'^window_view/(?P<slug>[\w_-]+)/$', views.NewWindowView.as_view(), name = 'window_view'),
	url(r'^view/(?P<slug>[\w_-]+)/$', views.InsideView.as_view(), name = 'view'),
]
