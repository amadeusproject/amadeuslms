from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.CreateLink.as_view(), name='create_link'),
    url(r'^deletelink/(?P<linkname>[\w_-]+)/$', views.deleteLink,name = 'delete_link'),
	url(r'^updatelink/(?P<linkname>[\w_-]+)/$', views.UpdateLink.as_view(),name = 'update_link'),
]
