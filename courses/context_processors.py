from .models import Course

def courses(request):
	if request.user.is_authenticated:
		context = {}

		if request.user.is_staff:
			context['courses_list'] = Course.objects.all()
		else:
			context['courses_list'] = Course.objects.filter(professors__in = [request.user])

		return context
	else:
		return request