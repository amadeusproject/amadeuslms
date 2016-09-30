from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^create/$', views.CreatePoll.as_view(), name='create_poll'),
	url(r'^update/(?P<slug>[\w\-_]+)/$', views.UpdatePoll.as_view(), name='update_poll'),

]
