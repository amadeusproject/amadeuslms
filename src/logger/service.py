from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils.current_user import get_current_user

from .defs import LOGGER_EXCLUDED_FIELDS
from .models import ActionLog


def entry_log(user, action, target_object=None, context=None, from_system=False):
  data = {
    "user": user,
    "action": action,
    "context": context or {},
    "from_system": from_system,
  }

  if target_object:
    data["content_type"] = ContentType.objects.get_for_model(target_object)
    data["object_id"] = target_object.pk

  return ActionLog.objects.create(**data)


class AuditableModel(models.Model):
  created_at = models.DateTimeField(
    auto_now_add=True, verbose_name=_("Data de criação")
  )
  updated_at = models.DateTimeField(
    auto_now=True, verbose_name=_("Data de atualização")
  )

  class Meta:
    abstract = True

  EXCLUDED_FIELDS = LOGGER_EXCLUDED_FIELDS

  def get_changes(self):
    if not self.pk:
      return None

    original = self.__class__.objects.get(pk=self.pk)

    if not original:
      return None

    changes = {}
    for field in self._meta.fields:
      if field.name in self.EXCLUDED_FIELDS:
        continue

      old_value = getattr(original, field.name)
      new_value = getattr(self, field.name)

      if str(old_value) != str(new_value):
        changes[field.name] = {"old": old_value, "new": new_value}

    return changes

  def save(self, *args, **kwargs):
    action_user = get_current_user()
    is_new = self.pk is None

    changes = None

    if not is_new:
      changes = self.get_changes()

    super().save(*args, **kwargs)

    if is_new or (changes and len(changes) > 0):
      action = "create" if is_new else "update"

      context = {}

      if changes:
        context["changes"] = changes

      entry_log(action_user, action, self, context)

  def delete(self, *args, **kwargs):
    action_user = get_current_user()

    context = {"object": str(self)}

    entry_log(action_user, "delete", self, context)

    super().delete(*args, **kwargs)
