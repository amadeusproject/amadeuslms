from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _

from .defs import EMAIL_VISIBILITY_CHOICES, user_directory_path
from .validators import (
  validate_email_format,
  validate_file_size,
  validate_image_extension,
)


class Account(AbstractBaseUser):
  email = models.EmailField(
    _("Endereço de email"),
    unique=True,
    validators=[validate_email_format],
    help_text=_("Seu endereço de email para acesso à plataforma"),
  )

  firstname = models.CharField(_("Nome"), max_length=255)
  lastname = models.CharField(_("Sobrenome"), max_length=255)

  is_support = models.BooleanField(_("Suporte"), default=False)
  is_staff = models.BooleanField(_("Administrador"), default=False)
  is_active = models.BooleanField(_("Ativo"), default=True)

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["firstname", "lastname"]

  objects = UserManager()

  class Meta:
    verbose_name = _("Conta do usuário")
    verbose_name_plural = _("Contas dos usuários")

  def email_user(self, subject, message, from_email=None, **kwargs):
    send_mail(subject, message, from_email, [self.email], **kwargs)


class User(models.Model):
  account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="user")

  socialname = models.CharField(_("Nome social"), max_length=255, blank=True, null=True)
  description = models.TextField(_("Biografia"), blank=True, null=True)
  avatar = models.ImageField(
    _("Imagem de perfil"),
    upload_to=user_directory_path,
    blank=True,
    null=True,
    validators=[validate_image_extension, validate_file_size],
  )
  show_email = models.IntegerField(
    _("Mostrar email?"),
    default=0,
    choices=EMAIL_VISIBILITY_CHOICES,
  )
  created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
  updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

  class Meta:
    verbose_name = _("Perfil do usuário")
    verbose_name_plural = _("Perfis dos usuários")
