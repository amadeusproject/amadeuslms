from django import template
from django.utils.translation import ugettext_lazy as _

from categories.models import Category
from subjects.models import Subject

register = template.Library()

@register.filter(name = 'is_coordinator')
def is_coordinator(user):
	cats = Category.objects.filter(coordinators = user)

	if len(cats) > 0:
		return ", ".join(cats.values_list('name', flat = True))

	return _('Is not a coordinator')

@register.filter(name = 'is_professor')
def is_professor(user):
	subs = Subject.objects.filter(professor = user)

	if len(subs) > 0:
		return ", ".join(subs.values_list('name', flat = True))

	return _('Is not a professor')

@register.filter(name = 'is_student')
def is_student(user):
	subs = Subject.objects.filter(students = user)

	if len(subs) > 0:
		return ", ".join(subs.values_list('name', flat = True))

	return _('Is not a student')
