from .models import Notification

def notifications(request):
	if request.user.is_authenticated:
		return {
		   'notifications': Notification.objects.filter(user= request.user, read=False).order_by('-datetime')
		}
	else:
		return request