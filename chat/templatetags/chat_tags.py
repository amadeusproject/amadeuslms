from django import template
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, F
from django.utils.translation import ugettext_lazy as _
from django.contrib.sessions.models import Session

from log.models import Log

from chat.models import TalkMessages, ChatVisualizations

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

@register.assignment_tag(name = 'chat_user')
def chat_user(user, chat):
	if chat.user_one == user:
		return chat.user_two

	return chat.user_one

@register.filter(name = 'last_message')
def last_message(chat):
	last_message = TalkMessages.objects.filter(talk = chat).order_by('-create_date')[0]

	return last_message.create_date

@register.filter(name = 'notifies')
def notifies(chat, user):
	total = ChatVisualizations.objects.filter(message__talk = chat, user = user).count()

	return total