""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework.documentation import include_docs_urls

from .views import index


urlpatterns = [
    url(r'^users/', include('users.urls', namespace = 'users')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name = 'home'),
    url(r'^api/', include('api.urls', namespace = 'api')),
    url(r'^categories/', include('categories.urls', namespace = 'categories')),
    url(r'^subjects/', include('subjects.urls', namespace = 'subjects')),
    url(r'^groups/', include('students_group.urls', namespace = 'groups')),
    url(r'^topics/', include('topics.urls', namespace = 'topics')),
    url(r'^chat/', include('chat.urls', namespace = 'chat')),
    url(r'^mural/', include('mural.urls', namespace = 'mural')),
    url(r'^webpages/', include('webpage.urls', namespace = 'webpages')),
    url(r'^ytvideo/', include('youtube_video.urls', namespace = 'youtube')),
    url(r'^file_links/', include('file_link.urls', namespace = 'file_links')),
    url(r'^goals/', include('goals.urls', namespace = 'goals')),
    url(r'^mailsender/', include('mailsender.urls', namespace = 'mailsender')),
    url(r'^security/', include('security.urls', namespace = 'security')),
    url(r'^themes/', include('themes.urls', namespace = 'themes')),
    url(r'^pendencies/', include('notifications.urls', namespace = 'notifications')),
    url(r'^links/', include('links.urls', namespace='links')),
    url(r'^pdf_files/', include('pdf_file.urls', namespace='pdf_files')),
    url(r'^webconferences/', include('webconference.urls', namespace = 'webconferences')),
    url(r'^news/', include('news.urls', namespace='news')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^analytics/', include('analytics.urls', namespace='analytics')),
    url(r'^dashboards/', include('dashboards.urls', namespace='dashboards')),
    url(r'^bulletin/', include('bulletin.urls', namespace='bulletin')),
    url(r'^api-docs/', include_docs_urls(title = 'REST Api Documentation')),
    #API
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    #S3Direct
    url(r'^s3direct/', include('s3direct.urls')),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'session_security/', include('session_security.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
