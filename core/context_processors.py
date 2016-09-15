from .models import Notification

def notifications(request):
	return {
	   'notifications': Notifications.objects.filter(user= request.user, read=False).order_by('-datetime')
	}