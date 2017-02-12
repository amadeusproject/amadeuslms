from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy

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
			return reverse_lazy('webpages:window_view', args = (), kwargs = {'slug': self.slug})

		return reverse_lazy('webpages:view', args = (), kwargs = {'slug': self.slug})

	def update_link(self):
		return 'webpages:update'

	def delete_link(self):
		return 'webpages:delete'

	def delete_message(self):
		return _('Are you sure you want delete the webpage')
