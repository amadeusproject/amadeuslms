from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^report/$', views.ReportView.as_view(), name='report'),
]