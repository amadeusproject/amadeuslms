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
	url(r'^general/$', views.GeneralView.as_view(), name='view_general'),
	url(r'^general/log/$', views.LogView.as_view(), name='view_general_log'),
	url(r'^analytics/$', views.GeneralManager.as_view(), name='view_manager_dashboard'),
	url(r'^categories/$', views.CategoryView.as_view(), name='view_categories'),
	url(r'^get_log_data/$', views.load_log_data, name='load_log_data'),
	url(r'^metrics/([\w_-]+)/([\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.other_metrics, name='other_metrics'),
	url(r'^tag/accessess/([\w_-]+)/([\w_-]+)/([\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.tag_accessess, name='tag_accessess'),
	url(r'^subjects/teacher/(?P<slug>[\w_-]+)/$', views.SubjectTeacher.as_view(), name='view_teacher'),
	url(r'^subjects/(?P<slug>[\w_-]+)/$', views.SubjectView.as_view(), name='view_subject'),
	url(r'^subjects/(?P<slug>[\w_-]+)/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})$', views.SubjectView.as_view(), name='view_subject_student'),
	url(r'^bubble_chart/(?P<slug>[\w_-]+)/$', views.most_active_users, name='bubble_chart'),
	url(r'^general_bubble_chart/$', views.most_active_users_general, name='general_bubble_chart'),
	url(r'^cloudydata/([\w_-]+)/([\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.cloudy_data, name='cloudy_data'),
	url(r'^cloudydata-period/([\w_-]+)/$', views.cloudy_data_period, name='cloudy_data_period'),
	url(r'^resources/(?P<slug>[\w_-]+)/$', views.resources_accesses_general, name='resources_chart'),
	url(r'^tag/accessess/([\w_-]+)/([\w_-]+)/([\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/([\w_-]+)/([\w_-]+)/$', views.tag_accessess_period, name='tag_accessess_period'),
	url(r'^heatmap_chart/(?P<slug>[\w_-]+)/$', views.heatmap_graph, name='heatmap_chart'),
	url(r'^general_heatmap_chart/$', views.general_heatmap_graph, name='general_heatmap_chart'),
	url(r'^general_logs_chart/$', views.general_logs_chart, name='general_logs_chart'),
	url(r'^general_bar_chart/$', views.get_general_active_users, name='general_bar_chart'),	
	url(r'^cloudydata/([\w_-]+)/([\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.cloudy_data, name='cloudy_data')
]
