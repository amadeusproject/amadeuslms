from django.db import models
from django.utils.translation import ugettext_lazy as _
from courses.models import Course
from users.models import User

class Subscribe(models.Model):
	user = models.ForeignKey(User, verbose_name = _('User'))
	course = models.ForeignKey(Course, verbose_name = _('Course'))
	subs_date = models.DateField(_('Subscription Date'), auto_now_add = True)
	create_date = models.DateField(_('Creation Date'), auto_now_add = True)

	class Meta:
		verbose_name = _('Subscription')
		verbose_name_plural = _('Subscriptions')
