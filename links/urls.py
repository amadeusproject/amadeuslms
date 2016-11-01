from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^create_link/(?P<slug>[\w_-]+)/$', views.CreateLink.as_view(), name='create_link'),
    url(r'^delete_link/(?P<slug>[\w_-]+)/$', views.DeleteLink.as_view(),name = 'delete_link'),
	url(r'^update_link/(?P<slug>[\w_-]+)/$', views.UpdateLink.as_view(),name = 'update_link'),
    url(r'^render-link/(?P<slug>[\w_-]+)/$', views.render_link, name='render_link'),
    url(r'^view_link/(?P<slug>[\w_-]+)/$',views.ViewLink.as_view(),name = 'view_link')
]
