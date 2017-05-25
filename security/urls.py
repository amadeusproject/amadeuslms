from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.SecuritySettings.as_view(), name = 'update'),
]