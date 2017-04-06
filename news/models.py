from django.db import models

# Create your models here.
from autoslug.fields import AutoSlugField

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


def validate_img_extension(value):
	valid_formats = ['image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png']

	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('File not supported.'))

class News(models.Model):
    title = models.CharField( _("Name"), unique = True,max_length= 200)
    slug = AutoSlugField(_("Slug"),populate_from='title',unique=True)
    image = models.ImageField(verbose_name = _('News Image'), upload_to = 'news/', validators = [validate_img_extension])
	content = models.TextField(_('Description'))
