from rolepermissions.shortcuts import assign_role
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.views.generic import CreateView
from django.http import HttpResponse
from  .forms import CreateUserForm
from users.models import User

def index(request):
	context = {
		'subscribed_courses': 'testando'
	}
	return render(request, "index.html", context)

class CreateUser(CreateView):
	model = User
	form_class = CreateUserForm
	template_name = 'register_user.html'

	success_url = reverse_lazy('core:home')

	def form_valid(self, form):
		form.save()
		assign_role(form.instance, 'student')

		messages.success(self.request, _('User successfully registered!'))
		
		return super(CreateUser, self).form_valid(form)

def create_account(request):
	return render(request, "create_account.html")

def lembrar_senha(request):
	return render(request, "lembrar_senha.html")
