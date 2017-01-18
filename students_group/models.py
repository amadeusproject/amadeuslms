from django.db import models
from autoslug.fields import AutoSlugField
from django.utils.translation import ugettext_lazy as _

from subjects.models import Subject
from users.models import User

class StudentsGroup(models.Model):
	name = models.CharField(_('Name'), max_length = 200)
	slug = AutoSlugField(_("Slug"), populate_from = 'name', unique = True)
	description = models.TextField(_('Description'), blank = True)
	subject = models.ForeignKey(Subject, verbose_name = _('Subject'), related_name = 'group_subject', null = True)
	participants = models.ManyToManyField(User, verbose_name = _('Participants'), related_name = 'group_participants', blank = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)

	class Meta:
		verbose_name = _('Students Group')
		verbose_name_plural = _('Students Groups')

	def __str__(self):
		return self.name