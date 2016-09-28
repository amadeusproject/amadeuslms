from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^to/poll/to/$', views.Poll.as_view(), name='poll'),

]
