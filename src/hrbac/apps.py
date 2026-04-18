from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HrbacConfig(AppConfig):
  default_auto_field = "django.db.models.BigAutoField"
  name = "hrbac"
  verbose_name = _("Controle de Acesso")
