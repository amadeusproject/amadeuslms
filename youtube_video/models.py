from django.db import models
from django.utils.translation import ugettext_lazy as _

from topics.models import Resource

class YTVideo(Resource):
	url = models.URLField(_('URL'), max_length = 250)

	class Meta:
		verbose_name = _('YTVideo')
		verbose_name_plural = _('YTVideos')

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
