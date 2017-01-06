from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^home/$', views.HomeView.as_view(), name='home'),
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<option>[\w_-]+)/$', views.IndexView.as_view(), name='index'),
	url(r'^create/(?P<slug>[\w_-]+)/$', views.SubjectCreateView.as_view(), name='create'),
	url(r'^replicate/(?P<subject_slug>[\w_-]+)/$', views.SubjectCreateView.as_view(), name='replicate'),
	url(r'^update/(?P<slug>[\w_-]+)/$', views.SubjectUpdateView.as_view(), name='update'),
]