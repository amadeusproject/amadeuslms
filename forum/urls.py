from django.conf.urls import url, include

from . import views


urlpatterns = [
	url(r'^$', views.ForumIndex.as_view(), name='index'),
]
