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
from django.contrib.auth import views as auth_views
from django.contrib import admin

from core import views

urlpatterns = [
	url(r'^$', auth_views.login, {'template_name': 'index.html'}, name='home'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'home'}, name='logout'),
	url(r'^nova_conta/$', views.nova_conta, name='nova_conta'),
	url(r'^lembrar_senha/$', views.lembrar_senha, name='lembrar_senha'),
    url(r'^app/', include('app.urls', namespace = 'app')),
    url(r'^admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)