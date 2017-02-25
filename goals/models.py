from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy

from topics.models import Resource

class Goals(Resource):
	presentation = models.TextField(_('Presentation'), blank = True)
	limit_submission_date = models.DateTimeField(_('Submission Limit Date'), null = True, blank = True)

	class Meta:
		verbose_name = _('Goal')
		verbose_name_plural = _('Goals')

	def __str__(self):
		return self.name

	def access_link(self):
		return reverse_lazy('file_links:download', args = (), kwargs = {'slug': self.slug})

	def update_link(self):
		return 'goals:update'

	def delete_link(self):
		return 'file_links:delete'

	def delete_message(self):
		return _('Are you sure you want delete the goals')

class GoalItem(models.Model):
	description = models.CharField(_('Description'), max_length = 255, blank = True)
	ref_value = models.IntegerField(_('Referential Value'))
	order = models.PositiveSmallIntegerField(_('Order'), null = True)
	goal = models.ForeignKey(Goals, verbose_name = _('Goal'), related_name = 'item_goal')