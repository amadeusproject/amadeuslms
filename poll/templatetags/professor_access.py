from django import template
from rolepermissions.verifications import has_role

register = template.Library()

@register.simple_tag
def professor_subject(subject, user):
    if (has_role(user,'system_admin')):
        return True

    if (user in subject.professors.all()):
        return True

    return False
