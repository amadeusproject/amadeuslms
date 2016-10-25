from django.conf.urls import url, include

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w_-]+)/$', views.CreateFile.as_view(), name='create_file'), # topic slug
	url(r'^update/(?P<slug>[\w_-]+)/$', views.UpdateFile.as_view(), name='update_file'), # file slug
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.DeleteFile.as_view(), name='delete_file'), # file slug
	url(r'^render-file/(?P<id>[0-9]+)/$', views.render_file, name='render_file'), # file slug

]