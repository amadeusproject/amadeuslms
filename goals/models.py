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
		if self.show_window:
			return reverse_lazy('goals:window_view', args = (), kwargs = {'slug': self.slug})

		return reverse_lazy('goals:view', args = (), kwargs = {'slug': self.slug})

	def update_link(self):
		return 'goals:update'

	def delete_link(self):
		return 'goals:delete'

	def delete_message(self):
		return _('Are you sure you want delete the %s topic goals specification')%(self.topic.name)

class GoalItem(models.Model):
	description = models.CharField(_('Description'), max_length = 255, blank = True)
	ref_value = models.IntegerField(_('Referential Value'))
	order = models.PositiveSmallIntegerField(_('Order'), null = True)
	goal = models.ForeignKey(Goals, verbose_name = _('Goal'), related_name = 'item_goal')

	class Meta:
		ordering = ['order']