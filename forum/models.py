from django.utils.translation import ugettext_lazy as _
from django.db import models

from autoslug.fields import AutoSlugField

from courses.models import Activity

"""
It's one kind of activity available for a Topic.
It works like a 'topic' of forum, which users can post to it and answer posts of it.
"""
class Forum(Activity):
	title = models.CharField(_('Title'), max_length = 100)
	description = models.TextField(_('Description'), blank = True)
	create_date = models.DateField(_('Create Date'), auto_now_add = True)

	class Meta:
		verbose_name = _('Forum')
		verbose_name_plural = _('Foruns')

	def __str__(self):
		return self.title
