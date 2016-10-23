from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^create_link/(?P<slug>[\w_-]+)/$', views.CreateLink.as_view(), name='create_link'),
    url(r'^deletelink/(?P<linkname>[\w_-]+)/$', views.deleteLink,name = 'delete_link'),
	url(r'^updatelink/(?P<slug>[\w_-]+)/$', views.UpdateLink.as_view(),name = 'update_link'),
    url(r'^render-link/(?P<id>[0-9]+)/$', views.render_link, name='render_link'),
    url(r'^view_link/(?P<slug>[\w_-]+)/$',views.ViewLink.as_view(),name = 'view_link')
]
