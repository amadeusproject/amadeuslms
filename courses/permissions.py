from rolepermissions.permissions import register_object_checker
from amadeus.roles import SystemAdmin, Professor

@register_object_checker()
def view_topic(role, user, topic):
    if (role == SystemAdmin):
        return True

    if (user in topic.subject.course.professors.all() and user in topic.subject.professors.all()):
        return True

    if (user in topic.subject.course.students.all() and user in topic.subject.students.all()):
        return True

    return False

@register_object_checker()
def edit_topic(role, user, topic):
    if (role == SystemAdmin):
        return True

    if (user == topic.owner):
        return True

    return False

@register_object_checker()
def view_subject(role, user, subject):
    if (role == SystemAdmin):
        return True

    if (user in subject.course.professors.all() and user in subject.professors.all()):
        return True

    if (user in subject.course.students.all() and user in subject.students.all()):
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
def delete_category(role, user, category):
    if (role == SystemAdmin or role == Professor):
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
