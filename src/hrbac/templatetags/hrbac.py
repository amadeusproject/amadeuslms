from django import template

from ..gatekeeper import has_resource_permission

register = template.Library()


@register.simple_tag
def has_permission(user, resource, *permissions):
  return has_resource_permission(user, resource, *permissions)
