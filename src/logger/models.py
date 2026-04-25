from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils.translation import gettext_lazy as _

from .defs import LOGGER_ACTION_CHOICES

UserModel = get_user_model()


class ActionLog(models.Model):
  user = models.ForeignKey(
    UserModel, on_delete=models.SET_NULL, null=True, verbose_name=_("Usuário")
  )
  action = models.CharField(
    max_length=100, verbose_name=_("Ação"), choices=LOGGER_ACTION_CHOICES
  )
  timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Data e hora"))

  module = models.ForeignKey(
    ContentType, on_delete=models.SET_NULL, null=True, verbose_name=_("Módulo")
  )
  object_id = models.PositiveIntegerField(null=True, verbose_name=_("ID do objeto"))
  target_object = GenericForeignKey("module", "object_id")
  is_resource = models.BooleanField(default=False, verbose_name=_("É recurso?"))

  from_system = models.BooleanField(
    default=False, verbose_name=_("Originou do sistema?")
  )

  context = models.JSONField(default=dict, blank=True, verbose_name=_("Contexto"))

  class Meta:
    verbose_name = _("Registro de ação")
    verbose_name_plural = _("Registros de ações")

    ordering = ["-timestamp"]

    indexes = [
      models.Index(fields=["user", "timestamp"]),
      models.Index(fields=["module", "object_id"]),
      GinIndex(fields=["context"], name="actionlog_context_gin_idx"),
    ]
