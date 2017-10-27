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
	url(r'^$', views.ListNewsView.as_view(), name='manage_news'),
	url(r'^view/(?P<slug>[\w_-]+)/$', views.VisualizeNews.as_view(), name = 'view'),
	url(r'^create/$', views.CreateNewsView.as_view(), name='create'),
	url(r'^update/(?P<slug>[\w_-]+)/$', views.UpdateNewsView.as_view(), name = 'update'),
	url(r'^search/$', views.SearchNewsView.as_view(), name = 'search'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.DeleteNewsView.as_view(), name='delete'),

]
