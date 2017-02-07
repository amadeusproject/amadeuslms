
"""amadeus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from .views import index


urlpatterns = [
    url(r'^users/', include('users.urls', namespace = 'users')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name = 'home'),
    url(r'^categories/', include('categories.urls', namespace = 'categories')),
    url(r'^subjects/', include('subjects.urls', namespace = 'subjects')),
    url(r'^groups/', include('students_group.urls', namespace = 'groups')),
    url(r'^topics/', include('topics.urls', namespace = 'topics')),
    url(r'^mural/', include('mural.urls', namespace = 'mural')),
    url(r'^webpages/', include('webpage.urls', namespace = 'webpages')),
    url(r'^ytvideo/', include('youtube_video.urls', namespace = 'youtube')),
    url(r'^file_links/', include('file_link.urls', namespace = 'file_links')),
    url(r'^mailsender/', include('mailsender.urls', namespace = 'mailsender')),
    url(r'^security/', include('security.urls', namespace = 'security')),
    url(r'^themes/', include('themes.urls', namespace = 'themes')),
    url(r'^pendencies/', include('notifications.urls', namespace = 'notifications')),
    url(r'^links/', include('links.urls', namespace='links')),
    url(r'^pdf_files/', include('pdf_file.urls', namespace='pdf_files')),
    #API
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    #S3Direct
    url(r'^s3direct/', include('s3direct.urls')),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'session_security/', include('session_security.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
