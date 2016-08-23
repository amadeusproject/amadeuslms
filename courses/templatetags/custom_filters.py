from django import template
import datetime
from subscriptions.models import Subscribe

register = template.Library()

@register.filter(expects_localtime=True)
def show_subscribe(course, user):
	actual = datetime.date.today()

	return  course.init_register_date <= actual <= course.end_register_date and not Subscribe.objects.filter(user = user, course = course)

@register.filter
def subscribed(course, user):
	return Subscribe.objects.filter(user = user, course = course)