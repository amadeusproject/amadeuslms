from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from courses.models import Course

@login_required
def index(request):
	context = {}

	context['courses'] = Course.objects.filter(user = request.user)

	return render(request, "home_app.html", context)
