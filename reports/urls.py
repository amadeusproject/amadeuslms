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
    url(r'^create/interactions/$', views.ReportView.as_view(), name='create_interaction'),
    url(r'^view/interactions/$', views.ViewReportView.as_view(), name='view_report'),
    url(r'^get/resources/$', views.get_resources, name='get_resource_and_tags'),
    url(r'^get/tags/$', views.get_tags, name='get_tags'),
    url(r'^post/download_report/$', views.download_report_csv, name="download_report_csv"),
    url(r'^post/download_report/excel$', views.download_report_xls, name="download_report_xls"),
]