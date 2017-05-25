from datetime import datetime

from themes.models import Themes
from notifications.models import Notification
from mural.models import MuralVisualizations
from chat.models import ChatVisualizations

def theme(request):
	context = {}

	theme = Themes.objects.get(id = 1)

	context['theme'] = theme
	if ("contrast_check" in request.COOKIES.keys()):
		context ['contrast_cookie'] = True
	else:
		context ['contrast_cookie'] = False
	
	return context

def notifies(request):
	context = {}

	notifications = 0

	if request.user.is_authenticated:
		notifications = Notification.objects.filter(creation_date = datetime.now(), viewed = False, user = request.user).count()

	context['notifications_count'] = notifications

	return context

def mural_notifies(request):
	context = {}

	notifications = 0

	if request.user.is_authenticated:
		notifications = MuralVisualizations.objects.filter(viewed = False, user = request.user).count()

	context['mural_notifications_count'] = notifications

	return context

def chat_notifies(request):
	context = {}

	notifications = 0

	if request.user.is_authenticated:
		notifications = ChatVisualizations.objects.filter(viewed = False, user = request.user).count()

	context['chat_notifications_count'] = notifications

	return context
