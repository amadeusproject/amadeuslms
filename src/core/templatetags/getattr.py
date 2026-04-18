from django import template

register = template.Library()


@register.filter
def get_attr(obj, key):
  return getattr(obj, key, None)
