from django import template
from datetime import datetime
from django.utils.translation import ugettext_lazy as _

from notifications.utils import get_resource_users
from notifications.models import Notification

register = template.Library()

@register.filter(name = 'warning_class')
def warning_class(level):
	if level == 1:
		class_name = "alert-low"
	elif level == 2:
		class_name = "alert-low"
	elif level == 3:
		class_name = "alert-medium"
	else:
		class_name = "alert-danger"

	return class_name

@register.filter(name = 'warning_msg')
def warning_msg(level):
	if level == 1:
		msg = _('You still did not realize this task')
	elif level == 2:
		msg = _('You still did not realize this task')
	elif level == 3:
		msg = _('This task is late')
	else:
		msg = _('You miss this task')

	return msg

@register.filter(name = 'done_percent')
def done_percent(notification):
	users = get_resource_users(notification.task.resource)
	notified = Notification.objects.filter(user__in = users.values_list('id', flat = True), creation_date = datetime.now(), task = notification.task).count()

	number_users = users.count()

	not_done = (notified * 100) / number_users

	return 100 - not_done