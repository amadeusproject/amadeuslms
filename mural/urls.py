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
	url(r'^$', views.GeneralIndex.as_view(), name='manage_general'),
	url(r'^categories/$', views.CategoryIndex.as_view(), name='manage_category'),
	url(r'^subjects/$', views.SubjectIndex.as_view(), name='manage_subject'),
	url(r'^create_gen/$', views.GeneralCreate.as_view(), name='create_general'),
	url(r'^create_cat/(?P<slug>[\w_-]+)/$', views.CategoryCreate.as_view(), name='create_category'),
	url(r'^create_sub/(?P<slug>[\w_-]+)/$', views.SubjectCreate.as_view(), name='create_subject'),
	url(r'^create_res/(?P<slug>[\w_-]+)/(?P<rslug>[\w_-]+)/$', views.ResourceCreate.as_view(), name='create_resource'),
	url(r'^update_gen/(?P<pk>[\w_-]+)/$', views.GeneralUpdate.as_view(), name='update_general'),
	url(r'^update_cat/(?P<pk>[\w_-]+)/$', views.CategoryUpdate.as_view(), name='update_category'),
	url(r'^update_sub/(?P<pk>[\w_-]+)/$', views.SubjectUpdate.as_view(), name='update_subject'),
	url(r'^delete_gen/(?P<pk>[\w_-]+)/$', views.GeneralDelete.as_view(), name='delete_general'),
	url(r'^delete_cat/(?P<pk>[\w_-]+)/$', views.CategoryDelete.as_view(), name='delete_category'),
	url(r'^delete_sub/(?P<pk>[\w_-]+)/$', views.SubjectDelete.as_view(), name='delete_subject'),
	url(r'^subject/(?P<slug>[\w_-]+)/$', views.SubjectView.as_view(), name='subject_view'),
	url(r'^resource/(?P<slug>[\w_-]+)/$', views.ResourceView.as_view(), name='resource_view'),
	url(r'^load_category/([\w_-]+)/$', views.load_category_posts, name='load_category'),
	url(r'^load_subject/([\w_-]+)/$', views.load_subject_posts, name='load_subject'),
	url(r'^view_log_cat/(?P<category>[\w_-]+)/$', views.mural_category_log, name = 'view_log_cat'),
	url(r'^view_log_sub/(?P<subject>[\w_-]+)/$', views.mural_subject_log, name = 'view_log_sub'),
	url(r'^favorite/([\w_-]+)/$', views.favorite, name='favorite'),
	url(r'^deleted/$', views.deleted_post, name='deleted_post'),
	url(r'^comment/(?P<post>[\w_-]+)/$', views.CommentCreate.as_view(), name='create_comment'),
	url(r'^update_comment/(?P<pk>[\w_-]+)/$', views.CommentUpdate.as_view(), name='update_comment'),
	url(r'^delete_comment/(?P<pk>[\w_-]+)/$', views.CommentDelete.as_view(), name='delete_comment'),
	url(r'^deleted_comment/$', views.deleted_comment, name='deleted_comment'),
	url(r'^render_comment/([\w_-]+)/([\w_-]+)/$', views.render_comment, name='render_comment'),
	url(r'^render_post/([\w_-]+)/([\w_-]+)/([\w_-]+)/$', views.render_post, name='render_post'),
	url(r'^load_comments/([\w_-]+)/([\w_-]+)/$', views.load_comments, name='load_comments'),
	url(r'^suggest_users/$', views.suggest_users, name='suggest_users'),
]