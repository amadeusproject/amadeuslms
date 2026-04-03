from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, FileExtensionValidator
from django.utils.translation import gettext_lazy as _

validate_email_format = EmailValidator(message=_("Informe um e-mail válido."))

validate_image_extension = FileExtensionValidator(
  allowed_extensions=["jpg", "jpeg", "png"],
  message=_("Somente imagens são permitidas."),
)


def validate_file_size(value):
  max_size = 5 * 1024 * 1024
  if value.size > max_size:
    raise ValidationError(_("O arquivo deve ter no máximo 5MB."))
