from django.db import models
from django.utils.translation import ugettext_lazy as _

from users.models import User
from pendencies.models import Pendencies

class Notification(models.Model):
	meta = models.DateTimeField(_('Meta'), null = True, blank = True)
	task = models.ForeignKey(Pendencies, verbose_name = _('Task'), related_name = 'notification_pendencies')
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = 'notification_user')
	level = models.IntegerField(_('Type'), choices = ((1, _('Type 1-A')), (2, _('Type 1-B')), (3, _('Type 2')), (4, _('Type 3'))))
	viewed = models.BooleanField(_('Visualized'), default = False)
	creation_date = models.DateField(_('Creation Date'), auto_now_add = True)

	def __str__(self):
		return self.task.get_action_display() + " " + str(self.task.resource)
