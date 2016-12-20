from django.http import Http404
from django.shortcuts import redirect

def index(request):
	if request.user.is_authenticated:
		raise Http404('<h1>Page not found</h1>') 
	else:
		return redirect('users:login')