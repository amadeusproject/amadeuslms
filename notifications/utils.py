from datetime import date
from django.utils import timezone
from django.db.models import Q

from log.models import Log
from pendencies.models import Pendencies
from users.models import User

from .models import Notification

def get_resource_users(resource):
	if resource.all_students:
		return resource.topic.subject.students.all()

	return User.objects.filter(Q(resource_students = resource) | Q(group_participants__resource_groups = resource)).distinct()

def set_notifications():
	pendencies = Pendencies.objects.filter(begin_date__date__lt = timezone.now(), resource__visible = True)

	for pendency in pendencies:
		users = get_resource_users(pendency.resource)
		subject_begin_date = pendency.resource.topic.subject.init_date
		pend_action = pendency.action
		resource_type = pendency.resource._my_subclass
		resource_key = resource_type + "_id"
		resource_id = pendency.resource.id

		for user in users:
			prev_notify = Notification.objects.filter(user = user, task = pendency).order_by("-creation_date")
			notify_type = 1

			if prev_notify.count() > 0:
				last_notify = prev_notify[0]

				if last_notify.creation_date == date.today():
					continue

				if last_notify.meta:
					if last_notify.creation_date < date.today() < last_notify.meta:
						continue

					notify_type = 2

			has_action = Log.objects.filter(user_id = user.id, action = pend_action, resource = resource_type, context__contains = {resource_key: resource_id}, datetime__date__gte = subject_begin_date).exists()

			if not has_action:
				if pendency.end_date:
					if timezone.now() > pendency.end_date:
						notify_type = 3

				if pendency.limit_date:
					if timezone.now() > pendency.limit_date:
						notify_type = 4

				
				notification = Notification()
				notification.user = user
				notification.level = notify_type
				notification.task = pendency

				notification.save()


