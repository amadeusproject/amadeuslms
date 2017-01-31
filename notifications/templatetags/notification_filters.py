from django import template
from datetime import datetime
from django.utils import timezone, formats
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

@register.filter(name = 'order_icon_class')
def order_icon_class(request, column):
	getvars = request.GET.copy()
	order = None
	class_name = "fa-sort"

	if 'order_by' in getvars:
		order = getvars['order_by']

	if not order:
		if column == "creation_date":
			class_name = "fa-sort-desc"
	else:
		if column in order:
			if "-" in order:
				class_name = "fa-sort-desc"
			else:
				class_name = "fa-sort-asc"

	return class_name

@register.filter(name = 'order_href')
def order_href(request, column):
	getvars = request.GET.copy()
	order_href = "-" + column
	order = None
	params = ""

	if 'order_by' in getvars:
		order = getvars['order_by']
		del getvars['order_by']
    
	if not order:
		if column == "creation_date":
			order_href = "creation_date"
	else:
		if column in order:
			if "-" in order:
				order_href = column
        
	if len(getvars) > 0:
		params = '&%s' % getvars.urlencode()

	return "?order_by=" + order_href + params

@register.filter(name = 'order_ajax')
def order_ajax(request, column):
	getvars = request.GET.copy()
	order_href = "-" + column
	order = None
	params = ""

	if 'order_by' in getvars:
		order = getvars['order_by']
		del getvars['order_by']
    
	if not order:
		if column == "creation_date":
			order_href = "creation_date"
	else:
		if column in order:
			if "-" in order:
				order_href = column
    
	return order_href

@register.filter(name = 'observation')
def observation(notification):
	msg = ''

	if notification.level == 1:
		if notification.meta:
			msg = _('Goal defined to task realization: %s')%(formats.date_format(notification.meta, "SHORT_DATETIME_FORMAT"))
	elif notification.level == 2:
		if notification.meta:
			if notification.meta < timezone.now():
				msg = _('Goal defined to task realization: %s')%(formats.date_format(notification.meta, "SHORT_DATETIME_FORMAT"))
			else:
				msg = _('New goal defined to task realization: %s')%(formats.date_format(notification.meta, "SHORT_DATETIME_FORMAT"))

	return msg