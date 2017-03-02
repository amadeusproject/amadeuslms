from django.conf.urls import url, include

# ========== API IMPORTS ============= #

from rest_framework import routers

from users.views import UserViewSet
from log.views import LogViewSet
from . import views

router = routers.DefaultRouter()
router.register(r'logs', LogViewSet)
router.register(r'usersapi', UserViewSet)

urlpatterns = [
	#API REST
    url(r'^report/$', views.ReportView.as_view(), name='report'),

    url(r'^', include(router.urls)),
]