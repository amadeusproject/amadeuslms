from django.db import models
from django.utils.translation import ugettext_lazy as _

class ElasticSearchSettings(models.Model):
	host = models.CharField(_("Host Url"), max_length = 250, blank=False, null = False)

	class Meta:
		verbose_name = _("Elastic Search Settings")
		verbose_name_plural = _("Elastic Search Settings")

	def __str__(self):
		return self.host
