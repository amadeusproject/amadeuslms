from rolepermissions.permissions import register_object_checker
from amadeus.roles import SystemAdmin

@register_object_checker()
def edit_topic(role, user, topic):
    if (role == SystemAdmin):
        return True

    if (user == topic.owner):
        return True

    return False

@register_object_checker()
def edit_subject(role, user, subject):
    if (role == SystemAdmin):
        return True

    if (user in subject.professors.all()):
        return True

    return False

@register_object_checker()
def delete_subject(role, user, subject):
    if (role == SystemAdmin):
        return True

    if (user in subject.professors.all()):
        return True

    return False

@register_object_checker()
def update_course(role, user, course):
    if (role == SystemAdmin):
        return True

    if (user in course.professors.all()):
        return True

    return False

@register_object_checker()
def delete_course(role, user, course):
    if (role == SystemAdmin):
        return True

    if (user in course.professors.all()):
        return True

    return False
