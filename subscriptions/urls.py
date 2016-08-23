from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^subscribe/$', views.subscribe, name='subscribe'),
	url(r'^cursos/subscribed/$', views.Index.as_view(), name='subscribed'),
	url(r'^cursos/(?P<slug>[\w_-]+)/participants/$', views.Participants.as_view(), name='participants'),
]