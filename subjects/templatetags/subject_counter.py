import datetime
from django import template
from django.db.models import Q

from chat.models import ChatVisualizations
from mural.models import MuralVisualizations
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
def notifies_number(subject, user):
	context = {}

	context['number'] = Notification.objects.filter(task__resource__topic__subject = subject, creation_date = datetime.datetime.now(), viewed = False, user = user).count()
	context['custom_class'] = 'pendencies_notify'
	
	return context

@register.inclusion_tag('subjects/badge.html')
def mural_number(subject, user):
	context = {}

	context['number'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__subjectpost__space = subject) | Q(comment__post__subjectpost__space = subject))).count()
	context['custom_class'] = 'mural_notify'
	
	return context

@register.inclusion_tag('subjects/badge.html')
def chat_number(subject, user):
	context = {}

	context['number'] = ChatVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & Q(message__talk__subjecttalk__space = subject)).count()
	context['custom_class'] = 'chat_notify'
	
	return context

@register.inclusion_tag('subjects/badge.html')
def resource_mural_number(resource, user):
	context = {}

	context['number'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__subjectpost__resource = resource) | Q(comment__post__subjectpost__resource = resource))).count()
	context['custom_class'] = 'mural_resource_notify'
	
	return context

@register.filter(name = 'aftertoday')
def after_today(date):
	if date > datetime.datetime.today().date():
		return True
	return False