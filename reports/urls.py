from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^create/interactions/$', views.ReportView.as_view(), name='create_interaction'),
    url(r'^view/interactions/$', views.ViewReportView.as_view(), name='view_report'),
]