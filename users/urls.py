from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^usuarios/$', views.Index.as_view(), name='manage'),
	url(r'^usuarios/criar/$', views.Create.as_view(), name='create'),
	url(r'^usuario/editar/(?P<username>[\w_-]+)/$', views.Update.as_view(), name='update'),
	url(r'^usuario/dados/(?P<username>[\w_-]+)/$', views.View.as_view(), name='view'),
	url(r'^perfil/$', views.Profile.as_view(), name='profile'),
	url(r'^perfil/editar/$', views.EditProfile.as_view(), name='edit_profile'),
]