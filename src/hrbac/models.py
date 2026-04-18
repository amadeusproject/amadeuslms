from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()


class Role(models.Model):
  name = models.CharField(max_length=100)
  slug = AutoSlugField(populate_from="name")
  description = models.TextField(blank=True)
  is_editable = models.BooleanField(default=True)
  is_removable = models.BooleanField(default=True)
  permissions = models.ManyToManyField(Permission, blank=True)

  class Meta:
    verbose_name = _("Papel")
    verbose_name_plural = _("Papeis")

  def __str__(self):
    return self.name


class UserModuleRole(models.Model):
  user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
  role = models.ForeignKey(Role, on_delete=models.CASCADE)
  module = models.ForeignKey(ContentType, on_delete=models.CASCADE)

  class Meta:
    verbose_name = _("Papel de usuário")
    verbose_name_plural = _("Papeis de usuário")

  def __str__(self):
    return f"{self.user} - {self.role} - {self.module}"
