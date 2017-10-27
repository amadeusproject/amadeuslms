""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='manage'),
	url(r'^category/(?P<slug>[\w_-]+)/$', views.IndexView.as_view(), name='manage_cat'),
	url(r'^set_goal/$', views.set_goal, name='set_goal'),
	url(r'^ajax/(?P<id>[\w_-]+)/$', views.AjaxNotifications.as_view(), name='ajax_view'),
	url(r'^ajax_history/(?P<id>[\w_-]+)/$', views.AjaxHistory.as_view(), name='ajax_history'),
	url(r'^view_log/(?P<subject>[\w_-]+)/$', views.pendencies_view_log, name = 'view_log'),
	url(r'^hist_log/(?P<subject>[\w_-]+)/$', views.pendencies_hist_log, name = 'hist_log'),
	url(r'^(?P<slug>[\w_-]+)/$', views.SubjectNotifications.as_view(), name='view'),
	url(r'^(?P<slug>[\w_-]+)/history/$', views.SubjectHistory.as_view(), name='history'),
]