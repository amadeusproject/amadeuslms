from django.contrib.auth.decorators import login_required
from .models import Subscribe

def subscribed_courses(request):
	context = {}

	if request.user.is_anonymous:
		context['subscribed_courses'] = None
	else:
		context['subscribed_courses'] = Subscribe.objects.filter(user = request.user)[:3] or None

	return context