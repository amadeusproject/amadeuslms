import datetime
from django import template
from django.db.models import Q

from notifications.models import Notification

register = template.Library()

@register.filter(name = 'subject_count')
def subject_count(category, user):
	total = 0
	
	if not user.is_staff:
		for subject in category.subject_category.all():
			if user in subject.students.all() or user in subject.professor.all() or user in subject.category.coordinators.all():
				total += 1
	else:		
		total = category.subject_category.count()

	return total

@register.inclusion_tag('subjects/badge.html')
def notifies_number(subject):
	context = {}

	context['number'] = Notification.objects.filter(task__resource__topic__subject = subject, creation_date = datetime.datetime.now()).count()
	
	return context

@register.filter(name = 'aftertoday')
def after_today(date):
	if date > datetime.datetime.today().date():
		return True
	return False