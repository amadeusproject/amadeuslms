from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.GeneralIndex.as_view(), name='manage_general'),
	url(r'^create_gen/$', views.GeneralCreate.as_view(), name='create_general'),
	url(r'^render_post/([\w_-]+)/$', views.render_gen_post, name='render_post_general'),
]