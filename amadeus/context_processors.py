from datetime import datetime

from themes.models import Themes
from notifications.models import Notification

def theme(request):
	context = {}

	theme = Themes.objects.get(id = 1)

	context['theme'] = theme

	return context

def notifies(request):
	context = {}

	notifications = 0

	if request.user.is_authenticated:
		notifications = Notification.objects.filter(creation_date = datetime.now(), viewed = False, user = request.user).count()

	context['notifications_count'] = notifications

	return context