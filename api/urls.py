""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.conf.urls import url, include

# ========== API IMPORTS ============= #
from rest_framework import routers

from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

from users.views import UserViewSet
from log.views import LogViewSet
from . import views

schema_view = get_schema_view(title = 'REST API', renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer])

router = routers.DefaultRouter()

router.register(r'logs', LogViewSet)
router.register(r'usersapi', UserViewSet)
router.register(r'users', views.LoginViewset)
router.register(r'subjects', views.SubjectViewset)
router.register(r'participants', views.ParticipantsViewset)
router.register(r'chat', views.ChatViewset)

urlpatterns = [
	#API REST
    url(r'^', include(router.urls)),
    url(r'^token$', views.getToken),
    url(r'^docs/', schema_view, name="docs"),
]