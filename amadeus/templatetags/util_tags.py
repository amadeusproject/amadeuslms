from django import template

register = template.Library()

@register.filter(name = 'zip')
def zip_lists(first, second):
	return zip(first, second)