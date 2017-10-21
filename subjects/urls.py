""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

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
	url(r'^restore/(?P<slug>[\w_-]+)/$', views.Restore.as_view(), name='restore'),
	url(r'^do_backup/(?P<subject>[\w_-]+)/$', views.realize_backup, name='do_backup'),
	url(r'^do_restore/(?P<subject>[\w_-]+)/$', views.realize_restore, name='do_restore'),
	url(r'^view/(?P<slug>[\w_-]+)/$', views.SubjectDetailView.as_view(), name='view'),
	url(r'^view/(?P<slug>[\w_-]+)/(?P<topic_slug>[\w_-]+)/$', views.SubjectDetailView.as_view(), name='topic_view'),
	url(r'^subscribe/(?P<slug>[\w_-]+)/$', views.SubjectSubscribeView.as_view(), name='subscribe'),
	url(r'^search/$', views.SubjectSearchView.as_view(), name='search'),
	url(r'^search/(?P<option>[\w_-]+)/$', views.SubjectSearchView.as_view(), name='search'),
	url(r'^load_subs/(?P<slug>[\w_-]+)/$', views.GetSubjectList.as_view(), name='load_view'),
	url(r'^view_log/(?P<subject>[\w_-]+)/$', views.subject_view_log, name = 'view_log'),
	url(r'^report/', include('reports.urls', namespace='reports')),
	url(r'^(?P<option>[\w_-]+)/$', views.IndexView.as_view(), name='index'),

]