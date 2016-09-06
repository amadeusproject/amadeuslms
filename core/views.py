from rolepermissions.shortcuts import assign_role
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import authenticate, login as login_user
from django.contrib.auth.mixins import LoginRequiredMixin
from .decorators import log_decorator
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView
from django.http import HttpResponse
from  .forms import RegisterUserForm
from users.models import User

def index(request):
	context = {
		'subscribed_courses': 'testando'
	}
	return render(request, "index.html", context)

class RegisterUser(CreateView):
	model = User
	form_class = RegisterUserForm
	template_name = 'register_user.html'

	success_url = reverse_lazy('core:home')

	def form_valid(self, form):
		form.save()
		assign_role(form.instance, 'student')

		messages.success(self.request, _('User successfully registered!'))
		
		return super(RegisterUser, self).form_valid(form)


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
