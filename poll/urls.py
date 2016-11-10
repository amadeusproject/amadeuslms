from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^view/(?P<slug>[\w\-_]+)/$', views.ViewPoll.as_view(), name='view_poll'), # poll slug
	url(r'^create/(?P<slug>[\w\-_]+)/$', views.CreatePoll.as_view(), name='create_poll'), # topic slug
	url(r'^update/(?P<slug>[\w\-_]+)/$', views.UpdatePoll.as_view(), name='update_poll'), # poll slug
	url(r'^delete/(?P<slug>[\w\-_]+)/$', views.DeletePoll.as_view(), name='delete_poll'), # poll
	url(r'^answer/$', views.AnswerPoll.as_view(), name='answer_poll'), # poll
	url(r'^answer-poll/(?P<slug>[\w\-_]+)/$', views.AnswerStudentPoll.as_view(), name='answer_student_poll'), # poll slug
	url(r'^poll-view/(?P<slug>[\w\-_]+)/$', views.render_poll_view, name='render_poll_view'), # poll slug
	url(r'^poll-edit/(?P<slug>[\w\-_]+)/$', views.render_poll_edit, name='render_poll_edit'), # poll slug
]
