from django.shortcuts import render
from django.http import HttpResponse

def index(request):
	context = {
		'subscribed_courses': 'testando'
	}
	return render(request, "index.html", context)