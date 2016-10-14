from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w\-_]+)/$', views.CreateExam.as_view(), name='create_exam'),
	url(r'^update/(?P<slug>[\w\-_]+)/$', views.UpdateExam.as_view(), name='update_exam'),
	url(r'^view/(?P<slug>[\w\-_]+)/$', views.ViewExam.as_view(), name='view_exam'),
	url(r'^delete/(?P<slug>[\w\-_]+)/$', views.DeleteExam.as_view(), name='delete_exam'),
]
