from django import template

from amadeus import permissions

register = template.Library()

@register.assignment_tag
def category_permissions(user, category):
	return permissions.has_category_permissions(user, category)

@register.assignment_tag
def subject_permissions(user, subject):
	return permissions.has_subject_permissions(user, subject)

@register.assignment_tag
def subject_view_permissions(user, subject):
	return permissions.has_subject_view_permissions(user, subject)

@register.assignment_tag
def resource_permissions(user, resource):
	return permissions.has_resource_permissions(user, resource)