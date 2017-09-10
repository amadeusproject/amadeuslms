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