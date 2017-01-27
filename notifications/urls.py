from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^(?P<slug>[\w_-]+)/$', views.SubjectNotifications.as_view(), name='view'),
]