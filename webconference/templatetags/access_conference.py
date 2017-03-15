import datetime
from django import template
from django.utils import timezone
register = template.Library()

@register.simple_tag
def access_conference(hour_conference):
	hour = datetime.datetime.now() + datetime.timedelta(minutes=10) # utilizado para poder começar a seção 10 min antes do tempo marcado
	hour_conference = hour_conference - datetime.timedelta(hours=3) # utilizado para converter a hora para UTC-3
	if (hour_conference.timetuple() < hour.timetuple()):
		return True
	return False
