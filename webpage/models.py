from django.db import models
from django.utils.translation import ugettext_lazy as _

from topics.models import Resource

class Webpage(Resource):
	content = models.TextField(_('Webpage Content'), blank = True)

	class Meta:
		verbose_name = _('WebPage')
		verbose_name_plural = _('WebPages')

	def __str__(self):
		return self.name

	def access_link(self):
		if self.show_window:
			return 'webpages:window_view'

		return 'webpages:view'

	def update_link(self):
		return 'webpages:update'

	def delete_link(self):
		return 'webpages:delete'
