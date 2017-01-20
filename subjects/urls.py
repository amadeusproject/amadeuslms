from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^home/$', views.HomeView.as_view(), name='home'),
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^category/(?P<slug>[\w_-]+)/$', views.IndexView.as_view(), name='cat_view'),
	url(r'^(?P<option>[\w_-]+)/$', views.IndexView.as_view(), name='index'),
	url(r'^create/(?P<slug>[\w_-]+)/$', views.SubjectCreateView.as_view(), name='create'),
	url(r'^replicate/(?P<subject_slug>[\w_-]+)/$', views.SubjectCreateView.as_view(), name='replicate'),
	url(r'^update/(?P<slug>[\w_-]+)/$', views.SubjectUpdateView.as_view(), name='update'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.SubjectDeleteView.as_view(), name='delete'),
	url(r'^view/(?P<slug>[\w_-]+)/$', views.SubjectDetailView.as_view(), name='view'),
	url(r'^subscribe/(?P<slug>[\w_-]+)/$', views.SubjectSubscribeView.as_view(), name='subscribe'),
	url(r'^search/$', views.SubjectSearchView.as_view(), name='search'),
]