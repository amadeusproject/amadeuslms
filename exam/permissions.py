from rolepermissions.permissions import register_object_checker
from amadeus.roles import SystemAdmin

@register_object_checker()
def edit_exam(role, user, exam):
    if (role == SystemAdmin):
        return True

    if (user in exam.topic.subject.professors.all()):
        return True

    return False

@register_object_checker()
def delete_exam(role, user, exam):
    if (role == SystemAdmin):
        return True

    if (user in exam.topic.subject.professors.all()):
        return True

    return False
