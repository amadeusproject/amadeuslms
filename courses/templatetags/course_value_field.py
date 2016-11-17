from django import template

register = template.Library()

"""
 Template tag to load all the foruns of a post
"""

@register.simple_tag
def value_field(course, field):
    value = ""
    if field == 'name':
        value = course.name
    elif field == 'content':
        value = course.content
    elif field == 'coordenator':
        value = course.coordenator
    elif field == 'category':
        value = course.category
    elif field == 'public':
        value = course.public

    return value


@register.simple_tag
def get_value_choice(value, choices):
    for v, name in choices:
        if (str(name) == str(value)): return v

    return ""

@register.simple_tag
def get_tag(field):
    field.value = "cacsdv"
    print (dir(field.field))
    print (dir(field.field.widget),field.name,"\n\n\n")
