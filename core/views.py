from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth import authenticate, login as login_user
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from .decorators import log_decorator
# from django.contrib.auth.views import LoginView

def index(request):
	context = {
		'subscribed_courses': 'testando'
	}
	return render(request, "index.html", context)

def create_account(request):
	return render(request, "create_account.html")

def remember_password(request):
	return render(request, "remember_password.html")

@log_decorator('Entrou no sistema')
def login(request):
	context = {}
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		usuario = authenticate(username=username, password=password)
		if usuario is not None:
			login_user(request, usuario)
			return redirect(reverse("app:index"))
		else:
			context["message"] = "Email ou senha incorretos!"
	return render(request,"index.html",context)


# class LoginClass(LoginView):
# 	template_name='index.html'
#
# 	def get_context_data(self, **kwargs):
# 		context = super(LoginClass,self).get_context_data(**kwargs)
# 		print ("deu certo")
# 		return context
