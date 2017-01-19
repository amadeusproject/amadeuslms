from django.db import models
from autoslug.fields import AutoSlugField
from django.utils.translation import ugettext_lazy as _

from subjects.models import Subject, Tag
from students_group.models import StudentsGroup
from users.models import User

class Topic(models.Model):
	name = models.CharField(_('Name'), max_length = 200)
	slug = AutoSlugField(_("Slug"), populate_from = 'name', unique = True)
	description = models.TextField(_('Description'), blank = True)
	repository = models.BooleanField(_('Repository'), default = False)
	visible = models.BooleanField(_('Visible'), default = True)
	subject = models.ForeignKey(Subject, verbose_name = _('Subject'), related_name = 'topic_subject', null = True)
	order = models.PositiveSmallIntegerField(_('Order'), null = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)

	class Meta:
		verbose_name = _('Topic')
		verbose_name_plural = _('Topics')
		ordering = ['order']

	def __str__(self):
		return self.name

class Resource(models.Model):
	name = models.CharField(_('Name'), max_length = 200)
	slug = AutoSlugField(_("Slug"), populate_from = 'name', unique = True)
	brief_description = models.TextField(_('Brief Description'), blank = True)
	show_window = models.BooleanField(_('Show in new window'), default = False)
	all_students = models.BooleanField(_('All Students'), default = False)
	visible = models.BooleanField(_('Visible'), default = True)
	order = models.PositiveSmallIntegerField(_('Order'), null = True)
	topic = models.ForeignKey(Topic, verbose_name = _('Topic'), related_name = "resource_topic", null = True)
	students = models.ManyToManyField(User, verbose_name = _('Students'), related_name = 'resource_students', blank = True)
	groups = models.ManyToManyField(StudentsGroup, verbose_name = _('Groups'), related_name = 'resource_groups', blank = True)
	tags = models.ManyToManyField(Tag, verbose_name = _('Markers'), related_name = 'resource_tags', blank = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)

	class Meta:
		verbose_name = _('Resource')
		verbose_name_plural = _('Resources')

	def __str__(self):
		return self.name
