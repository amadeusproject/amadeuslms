from django import template
from django.utils import timezone
from django.contrib.sessions.models import Session

register = template.Library()

@register.assignment_tag
def users_online():
	sessions = Session.objects.filter(expire_date__gte = timezone.now())

	uid_list = []

	# Build a list of user ids from that query
	for session in sessions:
		data = session.get_decoded()
		uid_list.append(data.get('_auth_user_id', None))
		
	return uid_list

@register.filter(name = 'is_online')
def is_online(user, online_list):
	if str(user.id) in online_list:
		print(str(user.id) in online_list)
		return "active"

	return ""