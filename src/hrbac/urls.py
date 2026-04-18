from django.urls import path

from .views import RoleMatrixView

app_name = "hrbac"

urlpatterns = [
  path("", RoleMatrixView.as_view(), name="role-permissions"),
]
