from django.conf.urls import url

from . import views


urlpatterns = [
	url(r'^$', views.ForumIndex.as_view(), name='index'),
	url(r'^create/$', views.CreateForumView.as_view(), name='create'),
	url(r'^update/(?P<pk>[\w_-]+)/$', views.UpdateForumView.as_view(), name='update'),
	url(r'^delete/(?P<pk>[\w_-]+)/$', views.ForumDeleteView.as_view(), name='delete'),
	url(r'^render_forum/([\w_-]+)/$', views.render_forum, name='render_forum'),
	url(r'^render_edit_forum/([\w_-]+)/$', views.render_edit_forum, name='render_edit_forum'),
	url(r'^forum_deleted/$', views.forum_deleted, name='deleted_forum'),
	url(r'^create_post/$', views.CreatePostView.as_view(), name='create_post'),
	url(r'^update_post/(?P<pk>[\w_-]+)/$', views.PostUpdateView.as_view(), name='update_post'),
	url(r'^delete_post/(?P<pk>[\w_-]+)/$', views.PostDeleteView.as_view(), name='delete_post'),
	url(r'^render_post/([\w_-]+)/$', views.render_post, name='render_post'),
	url(r'^post_deleted/$', views.post_deleted, name='deleted_post'),
	url(r'^post_answers/$', views.PostAnswerIndex.as_view(), name='post_answers'),
	url(r'^reply_post/$', views.CreatePostAnswerView.as_view(), name='reply_post'),
	url(r'^update_post_answer/(?P<pk>[\w_-]+)/$', views.PostAnswerUpdateView.as_view(), name='update_post_answer'),
	url(r'^render_post_answer/([\w_-]+)/$', views.render_post_answer, name='render_post_answer'),
	url(r'^delete_post_answer/(?P<pk>[\w_-]+)/$', views.PostAnswerDeleteView.as_view(), name='delete_answer'),
	url(r'^post_answer_deleted/$', views.answer_deleted, name='deleted_answer'),
	url(r'^(?P<slug>[\w_-]+)/$', views.ForumDetailView.as_view(), name='view'),
]
