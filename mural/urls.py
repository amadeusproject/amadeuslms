from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.GeneralIndex.as_view(), name='manage_general'),
	url(r'^create_gen/$', views.GeneralCreate.as_view(), name='create_general'),
	url(r'^update_gen/(?P<pk>[\w_-]+)/$', views.GeneralUpdate.as_view(), name='update_general'),
	url(r'^delete_gen/(?P<pk>[\w_-]+)/$', views.GeneralDelete.as_view(), name='delete_general'),
	url(r'^favorite/([\w_-]+)/$', views.favorite, name='favorite'),
	url(r'^deleted/$', views.deleted_post, name='deleted_post'),
	url(r'^comment/(?P<post>[\w_-]+)/$', views.CommentCreate.as_view(), name='create_comment'),
	url(r'^update_comment/(?P<pk>[\w_-]+)/$', views.CommentUpdate.as_view(), name='update_comment'),
	url(r'^render_comment/([\w_-]+)/([\w_-]+)/$', views.render_comment, name='render_comment'),
	url(r'^render_post/([\w_-]+)/([\w_-]+)/$', views.render_gen_post, name='render_post_general'),
	url(r'^suggest_users/$', views.suggest_users, name='suggest_users'),
]