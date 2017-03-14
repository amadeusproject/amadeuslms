from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.GeneralIndex.as_view(), name='manage_general'),
	url(r'^participants/$', views.GeneralParticipants.as_view(), name='participants_general'),
	url(r'^talk/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.GetTalk.as_view(), name = 'talk'),
	url(r'^participant/profile/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.ParticipantProfile.as_view(), name = 'profile'),
]