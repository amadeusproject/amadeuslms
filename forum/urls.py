from django.conf.urls import url, include

from . import views


urlpatterns = [
	url(r'^$', views.ForumIndex.as_view(), name='index'),
	url(r'^create$', views.CreateForumView.as_view(), name='create'),
	url(r'^posts$', views.PostIndex.as_view(), name='posts'),
	url(r'^post_answers$', views.PostAnswerIndex.as_view(), name='post_answers'),
	url(r'^reply_post$', views.CreatePostAnswerView.as_view(), name='reply_post'),
]
