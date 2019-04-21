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
    url(r'^users/', include(('users.urls', 'users'), namespace='users')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name='home'),
    url(r'^api/', include(('api.urls', 'api'), namespace='api')),
    url(r'^categories/', include(('categories.urls', 'categories'), namespace='categories')),
    url(r'^subjects/', include(('subjects.urls', 'subjects'), namespace='subjects')),
    url(r'^groups/', include(('students_group.urls', 'students_group'), namespace='groups')),
    url(r'^topics/', include(('topics.urls', 'topics'), namespace='topics')),
    url(r'^chat/', include(('chat.urls', 'chat'), namespace='chat')),
    url(r'^mural/', include(('mural.urls', 'mural'), namespace='mural')),
    url(r'^webpages/', include(('webpage.urls', 'webpage'), namespace='webpages')),
    url(r'^ytvideo/', include(('youtube_video.urls', 'youtube_video'), namespace='youtube')),
    url(r'^file_links/', include(('file_link.urls', 'file_link'), namespace='file_links')),
    url(r'^goals/', include(('goals.urls', "goals"), namespace='goals')),
    url(r'^mailsender/', include(('mailsender.urls', "mailsender"), namespace='mailsender')),
    url(r'^security/', include(('security.urls', "security"), namespace='security')),
    url(r'^themes/', include(('themes.urls', "themes"), namespace='themes')),
    url(r'^pendencies/',
        include(('notifications.urls', "notifications"), namespace='notifications')),
    url(r'^links/', include('links.urls', namespace='links')),
    url(r'^pdf_files/', include('pdf_file.urls', namespace='pdf_files')),
    url(r'^questionary/', include('questionary.urls', namespace='questionary')),
    url(r'^webconferences/', include('webconference.urls', namespace='webconferences')),
    url(r'^news/', include('news.urls', namespace='news')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^analytics/', include('analytics.urls', namespace='analytics')),
    url(r'^dashboards/', include('dashboards.urls', namespace='dashboards')),
    url(r'^bulletin/', include('bulletin.urls', namespace='bulletin')),
    url(r'^questions_database/', include('banco_questoes.urls', namespace='questions_database')),
    url(r'^api-docs/', include_docs_urls(title='REST Api Documentation')),
    # API
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'session_security/', include('session_security.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
