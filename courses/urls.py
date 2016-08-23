from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^cursos/$', views.IndexView.as_view(), name='manage'),
	url(r'^cursos/criar/$', views.CreateView.as_view(), name='create'),
	url(r'^cursos/editar/(?P<slug>[\w_-]+)/$', views.UpdateView.as_view(), name='update'),
	url(r'^cursos/(?P<slug>[\w_-]+)/$', views.View.as_view(), name='view'),
	url(r'^cursos/deletar/(?P<slug>[\w_-]+)/$', views.DeleteView.as_view(), name='delete'),
	url(r'^cursos/categoria/(?P<slug>[\w_-]+)/$', views.FilteredView.as_view(), name='filter'),
	url(r'^categorias/$', views.IndexCatView.as_view(), name='manage_cat'),
	url(r'^categorias/criar/$', views.CreateCatView.as_view(), name="create_cat"),
	url(r'^categorias/editar/(?P<slug>[\w_-]+)/$', views.UpdateCatView.as_view(), name='update_cat'),
	url(r'^categorias/(?P<slug>[\w_-]+)/$', views.ViewCat.as_view(), name='view_cat'),
	url(r'^categorias/deletar/(?P<slug>[\w_-]+)/$', views.DeleteCatView.as_view(), name='delete_cat'),
	url(r'^curso/(?P<slug>[\w_-]+)/modulos/$', views.ModulesView.as_view(), name='manage_mods'),
	url(r'^curso/(?P<slug>[\w_-]+)/modulos/cirar/$', views.CreateModView.as_view(), name='create_mods'),
	url(r'^curso/(?P<slug_course>[\w_-]+)/modulos/editar/(?P<slug>[\w_-]+)/$', views.UpdateModView.as_view(), name='update_mods'),
	url(r'^curso/(?P<slug_course>[\w_-]+)/modulos/deletar/(?P<slug>[\w_-]+)/$', views.DeleteModView.as_view(), name='delete_mods'),
]