from django.conf.urls import url

from . import views


urlpatterns = [
	url(r'^$', views.ForumIndex.as_view(), name='index'),
	url(r'^create/$', views.CreateForumView.as_view(), name='create'),
	url(r'^delete/(?P<pk>[\w_-]+)/$', views.ForumDeleteView.as_view(), name='delete'),
	url(r'^render_forum/([\w_-]+)/$', views.render_forum, name='render_forum'),
	url(r'^forum_deleted/$', views.forum_deleted, name='deleted_forum'),
	url(r'^create_post/$', views.CreatePostView.as_view(), name='create_post'),
	url(r'^update_post/(?P<pk>[\w_-]+)/$', views.PostUpdateView.as_view(), name='update_post'),
	url(r'^delete_post/(?P<pk>[\w_-]+)/$', views.PostDeleteView.as_view(), name='delete_post'),
	url(r'^render_post/([\w_-]+)/$', views.render_post, name='render_post'),
	url(r'^post_deleted/$', views.post_deleted, name='deleted_post'),
	url(r'^post_answers/$', views.PostAnswerIndex.as_view(), name='post_answers'),
	url(r'^reply_post/$', views.CreatePostAnswerView.as_view(), name='reply_post'),
	url(r'^(?P<slug>[\w_-]+)/$', views.ForumDetailView.as_view(), name='view'),
]
