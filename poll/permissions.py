from rolepermissions.permissions import register_object_checker
from amadeus.roles import SystemAdmin

@register_object_checker()
def edit_poll(role, user, poll):
    if (role == SystemAdmin):
        return True

    if (user in poll.topic.subject.professors.all()):
        return True

    return False

@register_object_checker()
def delete_poll(role, user, poll):
    if (role == SystemAdmin):
        return True

    if (user in poll.topic.subject.professors.all()):
        return True

    return False
