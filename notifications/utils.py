from datetime import datetime
from django.db.models import Q

from log.models import Log
from pendencies.models import Pendencies
from users.models import User

def get_resource_users(resource):
	if resource.all_students:
		return resource.topic.subject.students.all()

	return User.objects.filter(Q(resource_students = resource) | Q(group_participants__resource_groups = resource)).distinct()

def set_notifications():
	pendencies = Pendencies.objects.filter(begin_date__date__lt = datetime.now(), resource__visible = True)

	for pendency in pendencies:
		users = get_resource_users(pendency.resource)
		subject_begin_date = pendency.resource.topic.subject.init_date
		pend_action = pendency.action
		resource_type = pendency.resource._my_subclass
		resource_key = resource_type + "_id"
		resource_id = pendency.resource.id

		for user in users:
			has_action = Log.objects.filter(user_id = user.id, action = pend_action, resource = resource_type, context__contains = {resource_key: resource_id}, datetime__date__gte = subject_begin_date).exists()

			print(has_action)


