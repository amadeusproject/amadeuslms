from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w_-]+)/$', views.CreateView.as_view(), name = 'create'),
	url(r'^update/(?P<topic_slug>[\w_-]+)/(?P<slug>[\w_-]+)/$', views.UpdateView.as_view(), name = 'update'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.DeleteView.as_view(), name = 'delete'),
	url(r'^window_submit/(?P<slug>[\w_-]+)/$', views.NewWindowSubmit.as_view(), name = 'window_submit'),
	url(r'^view/(?P<slug>[\w_-]+)/$', views.InsideView.as_view(), name = 'view'),
	url(r'^submit/(?P<slug>[\w_-]+)/$', views.SubmitView.as_view(), name = 'submit'),
	url(r'^update_submit/(?P<slug>[\w_-]+)/$', views.UpdateSubmit.as_view(), name = 'update_submit'),
	url(r'^reports/(?P<slug>[\w_-]+)/$', views.Reports.as_view(), name = 'reports'),
	url(r'^answered_report/(?P<slug>[\w_-]+)/$', views.AnsweredReport.as_view(), name = 'answered_report'),
]
