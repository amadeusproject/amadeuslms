from django import template
from django.utils.translation import ugettext_lazy as _

from goals.models import MyGoals
from log.models import Log

register = template.Library()

@register.filter(name = 'groups')
def groups(user):
	groups = user.group_participants.values_list('name', flat = True)

	if groups.count() > 0:
		groups = list(groups)

		return ", ".join(groups)
	else:
		return "---"

@register.filter(name = 'creation_date')
def creation_date(user, goal):
	log = Log.objects.filter(user_id = user.id, action = 'submit', resource = 'goals', context__contains = {"goals_id": goal.id})

	if log.count() > 0:
		return log[0].datetime

	return ""

@register.filter(name = 'update_date')
def update_date(user, goal):
	log = Log.objects.filter(user_id = user.id, action = 'update_submit', resource = 'goals', context__contains = {"goals_id": goal.id})

	if log.count() > 0:
		return log[0].datetime

	return ""

@register.filter(name = 'my_goals')
def my_goals(user, goal):
	mine = list(MyGoals.objects.filter(user = user, item__goal = goal).values_list('value', flat = True))

	return  ', '.join(str(x) for x in mine)