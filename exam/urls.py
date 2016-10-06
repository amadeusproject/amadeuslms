from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w\-_]+)/$', views.CreateExam.as_view(), name='create_poll'),
	url(r'^update/(?P<slug>[\w\-_]+)/$', views.UpdateExam.as_view(), name='update_poll'),

]
