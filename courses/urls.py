from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^course/$', views.IndexView.as_view(), name='manage'),
	url(r'^course/create/$', views.CreateView.as_view(), name='create'),
	url(r'^course/edit/(?P<slug>[\w_-]+)/$', views.UpdateView.as_view(), name='update'),
	url(r'^course/(?P<slug>[\w_-]+)/$', views.View.as_view(), name='view'),
	url(r'^course/delete/(?P<slug>[\w_-]+)/$', views.DeleteView.as_view(), name='delete'),
	url(r'^course/category/(?P<slug>[\w_-]+)/$', views.FilteredView.as_view(), name='filter'),
	url(r'^categories/$', views.IndexCatView.as_view(), name='manage_cat'),
	url(r'^categories/create/$', views.CreateCatView.as_view(), name="create_cat"),
	url(r'^categories/edit/(?P<slug>[\w_-]+)/$', views.UpdateCatView.as_view(), name='update_cat'),
	url(r'^categories/(?P<slug>[\w_-]+)/$', views.ViewCat.as_view(), name='view_cat'),
	url(r'^categories/delete/(?P<slug>[\w_-]+)/$', views.DeleteCatView.as_view(), name='delete_cat'),
	url(r'^course/(?P<slug>[\w_-]+)/subjects/$', views.SubjectsView.as_view(), name='view_subject'),
	url(r'^course/(?P<slug>[\w_-]+)/topics/create/$', views.CreateTopicView.as_view(), name='create_topic'),
	url(r'^course/(?P<slug>[\w_-]+)/topics/update/$', views.UpdateTopicView.as_view(), name='update_topic'),
	# url(r'^course/(?P<slug>[\w_-]+)/modules/create/$', views.CreateModView.as_view(), name='create_mods'),
	# url(r'^course/(?P<slug_course>[\w_-]+)/modules/edit/(?P<slug>[\w_-]+)/$', views.UpdateModView.as_view(), name='update_mods'),
	# url(r'^course/(?P<slug_course>[\w_-]+)/modules/delete/(?P<slug>[\w_-]+)/$', views.DeleteModView.as_view(), name='delete_mods'),
	# url(r'^course/(?P<slug>[\w_-]+)/subject$', views.ViewSubject.as_view(), name='view_subject'),
]
