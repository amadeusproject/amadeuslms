from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w_-]+)/$', views.CreateLinkView.as_view(), name='create'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.DeleteLinkView.as_view(), name='delete'),
	url(r'^update/(?P<topic_slug>[\w_-]+)/(?P<slug>[\w_-]+)/$', views.UpdateLinkView.as_view(), name='update'),
	url(r'^view/(?P<slug>[\w_-]+)/$', views.RedirectUrl.as_view(), name='view')]