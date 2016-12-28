from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^create/$', views.CreateCategory.as_view(), name='create'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.DeleteCategory.as_view(), name='delete'),
	url(r'^replicate/(?P<slug>[\w_-]+)/$', views.CreateCategory.as_view(), name='replicate'),
	url(r'^update/(?P<slug>[\w_-]+)/$', views.UpdateCategory.as_view(), name='update'),
]