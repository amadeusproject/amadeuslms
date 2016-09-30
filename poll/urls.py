from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^create/$', views.CreatePoll.as_view(), name='create_poll'),

]
