from django.http import Http404
from django.shortcuts import redirect

def index(request):
	if request.user.is_authenticated:
		return redirect('categories:index')
	else:
		return redirect('users:login')