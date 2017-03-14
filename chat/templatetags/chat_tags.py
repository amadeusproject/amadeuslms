from django import template
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, F
from django.utils.translation import ugettext_lazy as _
from django.contrib.sessions.models import Session

from log.models import Log

register = template.Library()

@register.assignment_tag(name = 'is_online')
def is_online(user):
	expire_time = settings.SESSION_SECURITY_EXPIRE_AFTER
	now = timezone.now()
	
	activities = Log.objects.filter(user_id = user.id).order_by('-datetime')

	if activities.count() > 0:
		last_activity = activities[0]

		if last_activity.action != 'logout':
			if (now - last_activity.datetime).total_seconds() < expire_time:
				return "active"
			else:
				return "away"
	
	return ""

@register.filter(name = 'status_text')
def status_text(status):
	if status == "active":
		return _("Online")
	elif status == "away":
		return _('Away')
	else:
		return _("Offline")