
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
	context = {
		'subscribed_courses': 'testando'
	}
	return render(request, "index.html", context)

def create_account(request):
	return render(request, "create_account.html")

def lembrar_senha(request):
	return render(request, "lembrar_senha.html")
