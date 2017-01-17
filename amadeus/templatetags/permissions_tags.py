from django import template

from amadeus import permissions

register = template.Library()

@register.assignment_tag
def subject_permissions(user, subject):
	return permissions.has_subject_permissions(user, subject)