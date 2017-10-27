""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

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
def warning_msg(level, isnt_student):
	if level == 1:
		if isnt_student:
			msg = _('The student still did not realize this task')
		else:
			msg = _('You still did not realize this task')
	elif level == 2:
		if isnt_student:
			msg = _('The student still did not realize this task')
		else:
			msg = _('You still did not realize this task')
	elif level == 3:
		msg = _('This task is late')
	else:
		if isnt_student:
			msg = _('The student miss this task')
		else:
			msg = _('You miss this task')

	return msg

@register.filter(name = 'viewed_msg')
def viewed_msg(aware):
	if aware:
		msg = _('Yes')
	else:
		msg = _('No')

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

@register.filter(name = 'add_student')
def add_student(request, student):
	getvars = request.GET.copy()
	params = ""

	if not student is None:
		if not student == "":
			if 'selected_student' in getvars:
				del getvars['selected_student']
				   
			getvars['selected_student'] = student

			request.GET = getvars

	return request

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
			msg = _('Goal defined to task realization: %s')%(formats.date_format(notification.meta.astimezone(timezone.get_current_timezone()), "SHORT_DATETIME_FORMAT"))
	elif notification.level == 2:
		if notification.meta:
			if notification.meta < timezone.now():
				msg = _('Goal defined to task realization: %s')%(formats.date_format(notification.meta.astimezone(timezone.get_current_timezone()), "SHORT_DATETIME_FORMAT"))
			else:
				msg = _('New goal defined to task realization: %s')%(formats.date_format(notification.meta.astimezone(timezone.get_current_timezone()), "SHORT_DATETIME_FORMAT"))

	return msg