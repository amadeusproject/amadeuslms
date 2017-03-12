from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.GeneralIndex.as_view(), name='manage_general'),
	url(r'^participants/$', views.GeneralParticipants.as_view(), name='participants_general'),
]