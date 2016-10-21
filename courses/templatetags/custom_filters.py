from django import template
from rolepermissions.verifications import has_role

register = template.Library()

@register.filter
def show_subject_subscribe(user, subject):
	if not user is None:
		if user.is_authenticated:
			if has_role(user, 'student'):
				if not user in subject.students.all() and subject.show_subscribe:
					return  True

	return False

@register.filter
def show_course_subscribe(user, course):
	if not user is None:
		if user.is_authenticated:
			if has_role(user, 'student'):
				if not user in course.students.all() and course.show_subscribe:
					return  True

	return False