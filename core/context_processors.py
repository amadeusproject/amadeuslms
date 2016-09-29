from .models import Notification

def notifications(request):
	context = {}
	context['notifications'] = None
	if request.user.is_authenticated:
		return {
		   'notifications': Notification.objects.filter(user= request.user, read=False).order_by('-datetime')[0:5]
		}
	return context
