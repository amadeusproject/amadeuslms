from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.ListNewsView.as_view(), name='manage_news'),
	url(r'^view/(?P<slug>[\w_-]+)/$', views.VisualizeNews.as_view(), name = 'view'),
	url(r'^create/$', views.CreateNewsView.as_view(), name='create'),
	url(r'^update/(?P<slug>[\w_-]+)/$', views.UpdateNewsView.as_view(), name = 'update'),

]
