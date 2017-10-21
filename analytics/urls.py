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

	#"api" callls
	url(r'^most_used_tags/$', views.most_used_tags, name="most_used_tags"),
	url(r'^most_accessed_subjects/$', views.most_accessed_subjects, name="most_accessed_subjects"),
	url(r'^most_accessed_categories/$', views.most_accessed_categories, name = "most_accessed_categories"),
	url(r'^most_accessed_resources/$', views.most_accessed_resource_kind, name= "most_accessed_resources"),
	url(r'^most_active_users/$', views.most_active_users, name= "most_active_users"),
	url(r'^amount_active_users_per_day/$', views.most_active_users_in_a_month, name="most_active_users_in_a_month"),
	url(r'^get_days_of_the_week_log/$', views.get_days_of_the_week_log, name="get_days_of_the_week_log"),
	url(r'^get_category_tags/$', views.category_tags, name='get_category_tags'),
	url(r'^get_comments_count/$', views.get_amount_of_comments, name='get_amount_of_comments'),
]