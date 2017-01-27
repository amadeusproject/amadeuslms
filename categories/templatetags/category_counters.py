from django import template
from datetime import datetime

from notifications.models import Notification

register = template.Library()

@register.inclusion_tag('subjects/badge.html')
def notifies_cat_number(category, user):
	context = {}

	context['number'] = Notification.objects.filter(task__resource__topic__subject__category = category, creation_date = datetime.now(), viewed = False, user = user).count()
	
	return context