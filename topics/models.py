from django.db import models
from autoslug.fields import AutoSlugField
from django.utils.translation import ugettext_lazy as _

from subjects.models import Subject

class Topic(models.Model):
	name = models.CharField(_('Name'), max_length = 200)
	slug = AutoSlugField(_("Slug"), populate_from = 'name', unique = True)
	description = models.TextField(_('Description'), blank = True)
	repository = models.BooleanField(_('Repository'), default = False)
	visible = models.BooleanField(_('Visible'), default = True)
	subject = models.ForeignKey(Subject, verbose_name = _('Subject'), related_name = 'topic_subject')
	order = models.PositiveSmallIntegerField(_('Order'))
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)

	class Meta:
		verbose_name = _('Topic')
		verbose_name_plural = _('Topics')

	def __str__(self):
		return self.name