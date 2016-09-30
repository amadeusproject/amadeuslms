from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w\-_]+)/$', views.CreatePoll.as_view(), name='create_poll'), # topic slug
	url(r'^update/(?P<slug>[\w\-_]+)/$', views.UpdatePoll.as_view(), name='update_poll'), # poll slug

]
