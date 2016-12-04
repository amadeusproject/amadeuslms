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
    elif field == 'objectivies':
        value = course.objectivies
    elif field == 'content':
        value = course.content
    elif field == 'max_students':
        value = course.max_students
    elif field == 'init_register_date':
        value = course.init_register_date
    elif field == 'end_register_date':
        value = course.end_register_date
    elif field == 'init_date':
        value = course.init_date
    elif field == 'end_date':
        value = course.end_date
    elif field == 'coordenator':
        value = course.coordenator
    elif field == 'category':
        value = course.category
    elif field == 'professors':
        value = course.professors.all()
    elif field == 'students':
        value = course.students.all()
    elif field == 'public':
        value = course.public

    return value


@register.simple_tag
def get_value_choice(value, choices):
    for v, name in choices:
        if (str(name) == str(value)): return v

    return ""

@register.simple_tag
def value_subject_field(subject, field):
    value = ""
    if field == 'name':
        value = subject.name
    elif field == 'description':
        value = subject.description
    elif field == 'init_date':
        value = subject.init_date
    elif field == 'end_date':
        value = subject.end_date
    elif field == 'visible':
        value = subject.visible
    return value

@register.simple_tag
def value_topic_field(topic, field):
    value = ""
    if field == 'name':
        value = topic.name
    elif field == 'description':
        value = topic.description
    elif field == 'visible':
        value = topic.visible
    return value
