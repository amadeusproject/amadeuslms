from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy

def index(request):
	if request.user.is_authenticated:
		return redirect(reverse_lazy("subjects:home"))
	else:
		return redirect('users:login')