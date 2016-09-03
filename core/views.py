
from django.shortcuts import render
from django.http import HttpResponse
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



from django.contrib.auth import authenticate, login as login_user
from django.shortcuts import redirect
from django.urls import reverse

def login(request):
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		usuario = authenticate(username=username, password=password)
		print (dir(usuario))
		if usuario is not None:
			login_user(request, usuario)
			return redirect(reverse("app:index"))
	return render(request,"index.html")


# class LoginClass(LoginView):
# 	template_name='index.html'
#
# 	def get_context_data(self, **kwargs):
# 		context = super(LoginClass,self).get_context_data(**kwargs)
# 		print ("deu certo")
# 		return context
