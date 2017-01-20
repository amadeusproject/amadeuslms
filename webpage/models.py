from django.db import models
from autoslug.fields import AutoSlugField
from django.utils.translation import ugettext_lazy as _

from topics.models import Resource

class Webpage(Resource):
	content = models.TextField(_('Webpage Content'), blank = True)

	class Meta:
		verbose_name = _('WebPage')
		verbose_name_plural = _('WebPages')

	def __str__(self):
		return self.name