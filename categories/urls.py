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
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^create/$', views.CreateCategory.as_view(), name='create'),
	url(r'^delete/(?P<slug>[\w_-]+)/$', views.DeleteCategory.as_view(), name='delete'),
	url(r'^replicate/(?P<slug>[\w_-]+)/$', views.CreateCategory.as_view(), name='replicate'),
	url(r'^update/(?P<slug>[\w_-]+)/$', views.UpdateCategory.as_view(), name='update'),
	url(r'^view_log/(?P<category>[\w_-]+)/$', views.category_view_log, name = 'view_log')
]