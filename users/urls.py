from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='manage'),
	url(r'^criar/$', views.create, name='create'),
	url(r'^editar/([\w_-]+)/$', views.update, name='update'),
	url(r'^dados/([\w_-]+)/$', views.view, name='view'),
	url(r'^perfil/$', views.profile, name='profile'),
	url(r'^perfil/editar/$', views.edit_profile, name='edit_profile'),
]