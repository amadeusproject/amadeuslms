from .models import Course

def courses(request):
	context = {}
	context['courses_list'] = None
	if not request.user is None:
		if request.user.is_authenticated:
			if request.user.is_staff:
				context['courses_list'] = Course.objects.all()
			else:
				context['courses_list'] = Course.objects.filter(coordenator__in = [request.user])
			return context
	return context
