from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^view/(?P<slug>[\w\-_]+)/$', views.ViewPoll.as_view(), name='view_poll'), # poll slug
	url(r'^create/(?P<slug>[\w\-_]+)/$', views.CreatePoll.as_view(), name='create_poll'), # topic slug
	url(r'^update/(?P<slug>[\w\-_]+)/$', views.UpdatePoll.as_view(), name='update_poll'), # poll slug
	url(r'^delete/(?P<slug>[\w\-_]+)/$', views.DeletePoll.as_view(), name='delete_poll'), # poll
	url(r'^answer/$', views.AnswerPoll.as_view(), name='answer_poll'), # poll
]
