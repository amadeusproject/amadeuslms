from django import template
from links.models import Link
register = template.Library()

@register.filter('class_name')
def class_name(obj):
	return obj._my_subclass

@register.filter('resource_link')
def resource_link(resource):
	link = Link.objects.get(id=resource.id)
	return link.link_url