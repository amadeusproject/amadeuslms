from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.AppIndex.as_view(), name='index'),
    url(r'^settings/$', views.AmadeusSettings.as_view(), name='settings'),
]
