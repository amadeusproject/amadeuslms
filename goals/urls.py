""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


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
	url(r'^unanswered_report/(?P<slug>[\w_-]+)/$', views.UnansweredReport.as_view(), name = 'unanswered_report'),
	url(r'^history_report/(?P<slug>[\w_-]+)/$', views.HistoryReport.as_view(), name = 'history_report'),
	url(r'^view_log/(?P<goal>[\w_-]+)/(?P<report>[\w_-]+)/$', views.reports_log, name = 'reports_log'),
    url(r'^chart/(?P<slug>[\w_-]+)/$', views.StatisticsView.as_view(), name = 'get_chart'),
    url(r'^send-message/(?P<slug>[\w_-]+)/$', views.SendMessage.as_view(), name = 'send_message'),
]
