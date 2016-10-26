from rolepermissions.permissions import register_object_checker
from amadeus.roles import SystemAdmin

@register_object_checker()
def view_forum(role, user, forum):
    if (role == SystemAdmin):
        return True

    if (user in forum.topic.subject.professors.all() or user in forum.topic.subject.students.all()):
        return True

    return False

@register_object_checker()
def edit_forum(role, user, forum):
    if (role == SystemAdmin):
        return True

    if (user in forum.topic.subject.professors.all()):
        return True

    return False

@register_object_checker()
def delete_forum(role, user, forum):
    if (role == SystemAdmin):
        return True

    if (user in forum.topic.subject.professors.all()):
        return True

    return False
