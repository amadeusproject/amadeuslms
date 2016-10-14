from django import template

from forum.models import Forum

register = template.Library()

"""
 Template tag to load all the foruns of a post
"""

@register.filter
def value(dictionary, key):
    return dictionary[key]
