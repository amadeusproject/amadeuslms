from django.conf.urls import url, include
from . import views

urlpatterns = [
	url(r'^home/$', views.HomeView.as_view(), name='home'),
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^category/(?P<slug>[\w_-]+)/$', views.IndexView.as_view(), name='cat_view'),
	url(r'^create/(?P<slug>[\w_-]+)/$', views.SubjectCreateView.as_view(), name='create'),
	url(r'^replicate/(?P<subject_slug>[\w_-]+)/$', views.SubjectCreateView.as_view(), name='replicate'),
	url(r'^update/(?P<slug>[\w_-]+)/$', views.SubjectUpdateView.as_view(), name='update'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.SubjectDeleteView.as_view(), name='delete'),
	url(r'^backup/(?P<slug>[\w_-]+)/$', views.Backup.as_view(), name='backup'),
	url(r'^do_backup/(?P<subject>[\w_-]+)/$', views.realize_backup, name='do_backup'),
	url(r'^view/(?P<slug>[\w_-]+)/$', views.SubjectDetailView.as_view(), name='view'),
	url(r'^view/(?P<slug>[\w_-]+)/(?P<topic_slug>[\w_-]+)/$', views.SubjectDetailView.as_view(), name='topic_view'),
	url(r'^subscribe/(?P<slug>[\w_-]+)/$', views.SubjectSubscribeView.as_view(), name='subscribe'),
	url(r'^search/$', views.SubjectSearchView.as_view(), name='search'),
	url(r'^search/(?P<option>[\w_-]+)/$', views.SubjectSearchView.as_view(), name='search'),
	url(r'^load_subs/(?P<slug>[\w_-]+)/$', views.GetSubjectList.as_view(), name='load_view'),
	url(r'^view_log/(?P<subject>[\w_-]+)/$', views.subject_view_log, name = 'view_log'),
	url(r'^most_accessed_subjects/$', views.most_acessed_subjects, name='most_acessed'),
	url(r'^report/', include('reports.urls', namespace='reports')),
	url(r'^(?P<option>[\w_-]+)/$', views.IndexView.as_view(), name='index'),

]