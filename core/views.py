from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth import authenticate, login as login_user
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .decorators import log_decorator

def remember_password(request):
	return render(request, "remember_password.html")

@log_decorator('Entrou no sistema')
def login(request):
	context = {}
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login_user(request, user)
			return redirect(reverse("app:index"))
		else:
			context["message"] = _("E-mail or password are incorrect!")
	return render(request,"index.html",context)


# class LoginClass(LoginView):
# 	template_name='index.html'
#
# 	def get_context_data(self, **kwargs):
# 		context = super(LoginClass,self).get_context_data(**kwargs)
# 		print ("deu certo")
# 		return context
