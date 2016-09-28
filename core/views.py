from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import authenticate, login as login_user
from django.contrib.auth.mixins import LoginRequiredMixin
from .decorators import log_decorator
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView
from django.http import HttpResponse
from django.core.mail import send_mail,BadHeaderError
from django.conf import settings
from core.mixins import NotificationMixin
from .models import Notification
from rolepermissions.shortcuts import assign_role

from .forms import RegisterUserForm
from .decorators import log_decorator, notification_decorator

from users.models import User


def index(request):
	context = {
		'subscribed_courses': 'testando'
	}
	return render(request, "index.html", context)


class RegisterUser(CreateView, NotificationMixin):
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
	context = {}
	if request.POST:
		email = request.POST['email']
		registration = request.POST['registration']
		if email and registration:
			subject = _('Recover your password')
			message = _('Hello %s, \nRecover your password to use your account.\nNumber of registration: %s\nLink for recuver password.\n\nRespectfully,\nTeam Amadeus.' % (request.user,registration))
			try:
				send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email],fail_silently=False)
				context['success'] = 'Email successfully sent'
			except BadHeaderError:
				context['email'] = email
				context['registration'] = registration
				context['danger'] = 'E-mail does not send'
		else:
			context['email'] = email
			context['registration'] = registration
			context['danger'] = 'E-mail does not send'
	return render(request, "remember_password.html",context)

@notification_decorator(message='just connected')
@log_decorator('Acessar', 'Sistema')
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
			messages.add_message(request, messages.ERROR, _('E-mail or password are incorrect.'))
			context["username"] = username
	elif request.user.is_authenticated:
		return redirect(reverse('app:index'))

	return render(request,"index.html",context)



def processNotification(self, notificationId):
	notification = Notification.objects.get(id= notificationId)
	notification.read = True
	notification.save()
	return redirect(notification.action_resource.resource.url)

# class LoginClass(LoginView):
# 	template_name='index.html'
#
# 	def get_context_data(self, **kwargs):
# 		context = super(LoginClass,self).get_context_data(**kwargs)
# 		print ("deu certo")
# 		return context
