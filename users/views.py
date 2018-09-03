""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as _u
from django.db.models import Q, Count

from braces import views as braces_mixins

from security.models import Security

from log.decorators import log_decorator
from log.mixins import LogMixin
from log.models import Log
from django.http import JsonResponse
from .models import User
from .utils import has_dependencies
from .forms import RegisterUserForm, ProfileForm, UserForm, ChangePassForm, PassResetRequest, SetPasswordForm

#USER STATUS NOTIFICATION
from channels import Group
import json

#RECOVER PASS IMPORTS
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend

from mailsender.models import MailSender
import os
#API IMPORTS
from rest_framework import viewsets
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.contrib.rest_framework.permissions import IsAuthenticatedOrTokenHasScope

# ================ ADMIN =======================
class UsersListView(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'users/list.html'
	context_object_name = 'users'
	paginate_by = 10

	def get_queryset(self):
		users = User.objects.all().order_by('social_name','username').exclude(email = self.request.user.email)

		return users

	def get_context_data (self, **kwargs):
		context = super(UsersListView, self).get_context_data(**kwargs)
		context['title'] = _('Manage Users')
		context['settings_menu_active'] = "settings_menu_active"

		return context

class SearchView(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'users/search.html'
	context_object_name = 'users'
	paginate_by = 10

	def dispatch(self, request, *args, **kwargs):
		search = self.request.GET.get('search', '')

		if search == '':
			return redirect(reverse_lazy('users:manage'))

		return super(SearchView, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		search = self.request.GET.get('search', '')

		users = User.objects.filter(Q(username__icontains = search) | Q(last_name__icontains = search) | Q(social_name__icontains = search) | Q(email__icontains = search)).distinct().order_by('social_name','username').exclude(email = self.request.user.email)

		return users

	def get_context_data (self, **kwargs):
		context = super(SearchView, self).get_context_data(**kwargs)
		context['title'] = _('Search Users')
		context['search'] = self.request.GET.get('search')
		context['settings_menu_active'] = "settings_menu_active"

		return context

class CreateView(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = 'user'
	log_action = 'create'
	log_resource = 'user'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'users/create.html'
	form_class = UserForm
	context_object_name = 'acc'
	success_url = reverse_lazy('users:manage')

	def form_valid(self, form):
		self.object = form.save()

		msg = _('User "%s" created successfully')%(self.object.get_short_name() )

		self.log_context['user_id'] = self.object.id
		self.log_context['user_name'] = self.object.get_short_name()
		self.log_context['user_email'] = self.object.email

		super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		messages.success(self.request, msg)

		return super(CreateView, self).form_valid(form)

	def get_context_data (self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)
		context['title'] = _("Add User")
		context['settings_menu_active'] = "settings_menu_active"

		return context

class UpdateView(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, LogMixin, generic.UpdateView):
	log_component = 'user'
	log_action = 'update'
	log_resource = 'user'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'users/update.html'
	slug_field = 'email'
	slug_url_kwarg = 'email'
	context_object_name = 'acc'
	model = User
	form_class = UserForm
	success_url = reverse_lazy('users:manage')

	def get_form_kwargs(self):
		kwargs = super(UpdateView, self).get_form_kwargs()

		kwargs.update({'is_edit': True})

		return kwargs

	def form_valid(self, form):
		self.object = form.save(commit = False)

		self.object.save()

		msg = _('User "%s" updated successfully')%(self.object.get_short_name())

		self.log_context['user_id'] = self.object.id
		self.log_context['user_name'] = self.object.get_short_name()
		self.log_context['user_email'] = self.object.email

		super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		messages.success(self.request, msg)

		return super(UpdateView, self).form_valid(form)

	def get_context_data (self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)
		context['title'] = _("Update User")
		context['settings_menu_active'] = "settings_menu_active"

		return context

class DeleteView(braces_mixins.LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = 'user'
	log_action = 'delete'
	log_resource = 'user'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'users/delete.html'
	model = User
	slug_url_kwarg = 'email'
	context_object_name = 'acc'

	def dispatch(self, request, *args, **kwargs):
		email = self.kwargs.get('email', None)

		if not email is None:
			if not request.user.is_staff:
				return redirect(reverse_lazy('subjects:home'))

		return super(DeleteView, self).dispatch(request, *args, **kwargs)

	def get_object(self):
		email = self.kwargs.get('email', None)

		if email is None:
			user = get_object_or_404(User, email = self.request.user.email)
		else:
			user = get_object_or_404(User, email = email)

		return user

	def delete(self, request, *args, **kwargs):
		email = self.kwargs.get('email', None)
		user = self.get_object()



		if email is None:
			self.log_action = 'remove_account'

			success_url = reverse_lazy('users:login')
			error_url = reverse_lazy('users:profile')
		else:
			self.log_context['user_id'] = user.id
			self.log_context['user_name'] = user.get_short_name()
			self.log_context['user_email'] = user.email

			success_url = reverse_lazy('users:manage')
			error_url = reverse_lazy('users:manage')

		success_msg = _('User removed successfully!')
		error_msg = _('Could not remove the account. The user is attach to one or more functions (administrator, coordinator, professor ou student) in the system.')

		if has_dependencies(user):
			self.log_context['dependencies'] = True

			messages.error(self.request, error_msg)

			redirect_url = redirect(error_url)
		else:
			self.log_context['dependencies'] = False

			if user.image:
				image_path_to_delete = user.image.path
			else:
				image_path_to_delete = None

			user.delete()

			messages.success(self.request, success_msg)
			
			if not image_path_to_delete is None:
				#deleting the user image
				os.remove(image_path_to_delete)
				
			redirect_url = redirect(success_url)

		super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return redirect_url

	def get_context_data(self, **kwargs):
		context = super(DeleteView, self).get_context_data(**kwargs)
		context['title'] = _('Delete Account')
		context['email'] = self.kwargs.get('email', None)

		return context

	def render_to_response(self, context, **response_kwargs):
		email = self.kwargs.get('email', None)

		if email is None:
			template = 'users/delete_account.html'
		else:
			context['settings_menu_active'] = "settings_menu_active"
			template = 'users/delete.html'

		return self.response_class(request = self.request, template = template, context = context, using = self.template_engine, **response_kwargs)

class ChangePassView(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'users/change_password.html'
	slug_field = 'email'
	slug_url_kwarg = 'email'
	context_object_name = 'acc'
	model = User
	form_class = ChangePassForm
	success_url = reverse_lazy('users:profile')

	def get_form_kwargs(self):
		kwargs = super(ChangePassView, self).get_form_kwargs()

		kwargs.update({'user': self.request.user})
		kwargs.update({'request': self.request})

		return kwargs

	def get_object(self):
		user = get_object_or_404(User, email = self.request.user.email)

		return user

	def form_valid(self, form):
		form.save()

		messages.success(self.request, _('Password changed successfully!'))

		return super(ChangePassView, self).form_valid(form)

	def get_context_data (self, **kwargs):
		context = super(ChangePassView, self).get_context_data(**kwargs)
		context['title'] = _("Change Password")

		return context

class Profile(LoginRequiredMixin, generic.DetailView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	context_object_name = 'acc'
	template_name = 'users/profile.html'

	def get_object(self):
		user = get_object_or_404(User, email = self.request.user.email)

		return user

	def get_context_data (self, **kwargs):
		context = super(Profile, self).get_context_data(**kwargs)
		context['title'] = _("Profile")

		return context

class UpdateProfile(LoginRequiredMixin, generic.edit.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'users/edit_profile.html'
	form_class = ProfileForm
	success_url = reverse_lazy('users:profile')

	def get_object(self):
		user = get_object_or_404(User, email = self.request.user.email)

		return user

	def get_context_data(self, **kwargs):
		context = super(UpdateProfile, self).get_context_data(**kwargs)
		context['title'] = _('Update Profile')

		return context

	def form_valid(self, form):
		form.save()
		messages.success(self.request, _('Profile edited successfully!'))

		return super(UpdateProfile, self).form_valid(form)

class RegisterUser(generic.edit.CreateView):
	model = User
	form_class = RegisterUserForm
	template_name = 'users/register.html'

	success_url = reverse_lazy('users:login')

	def get_context_data(self, **kwargs):
		context = super(RegisterUser, self).get_context_data(**kwargs)
		context['title'] = _('Sign Up')

		return context

	def form_valid(self, form):
		form.save()

		messages.success(self.request, _('User successfully registered!'))

		return super(RegisterUser, self).form_valid(form)

	def dispatch(self, request, *args, **kwargs):
		security = Security.objects.get(id = 1)

		if security.allow_register:
			return redirect(reverse_lazy('users:login'))

		return super(RegisterUser, self).dispatch(request, *args, **kwargs)

class ForgotPassword(generic.FormView):
	template_name = "users/forgot_password.html"
	success_url = reverse_lazy('users:login')
	form_class = PassResetRequest

	def get_context_data(self, **kwargs):
		context = super(ForgotPassword, self).get_context_data(**kwargs)
		context['title'] = _('Forgot Password')

		return context

	def post(self, request, *args, **kwargs):
		form = self.get_form()

		if form.is_valid():
			email = form.cleaned_data['email']

			users = User.objects.filter(email = email)

			if users.exists():
				for user in users:
					uid = urlsafe_base64_encode(force_bytes(user.pk))
					token = default_token_generator.make_token(user)

					c = {
						'request': request,
						'title': _('Recover Password'),
						'email': user.email,
						'domain': request.build_absolute_uri(reverse("users:reset_password_confirm", kwargs = {'uidb64': uid, 'token':token})), #or your domain
						'site_name': 'Amadeus',
						'user': user,
						'protocol': 'http',
					}

					subject_template_name = 'registration/password_reset_subject.txt'
					email_template_name = 'recover_pass_email_template.html'

					subject = loader.render_to_string(subject_template_name, c)
	                # Email subject *must not* contain newlines
					subject = ''.join(subject.splitlines())
					email = loader.render_to_string(email_template_name, c)

					mailsender = MailSender.objects.latest('id')

					if mailsender.hostname == "example.com":
						send_mail(subject, email, settings.DEFAULT_FROM_EMAIL , [user.email], fail_silently=False)
					else:
						if mailsender.crypto == 3 or mailsender.crypto == 4:
							tls = True
						else:
							tls = False

						backend = EmailBackend(
									host = mailsender.hostname, port = mailsender.port, username = mailsender.username,
									password = mailsender.password, use_tls = tls
								)

						mail_msg = EmailMessage(subject = subject, body = email, to = [user.email], connection = backend)

						mail_msg.send()

				result = self.form_valid(form)
				messages.success(request, _("Soon you'll receive an email with instructions to set your new password. If you don't receive it in 24 hours, please check your spam box."))

				return result
			messages.error(request, _('No user is associated with this email address'))

		result = self.form_invalid(form)

		return result

class PasswordResetConfirmView(generic.FormView):
	template_name = "users/new_password.html"
	success_url = reverse_lazy('users:login')
	form_class = SetPasswordForm

	def get_context_data(self, **kwargs):
		context = super(PasswordResetConfirmView, self).get_context_data(**kwargs)
		context['title'] = _('Reset Password')

		return context

	def post(self, request, uidb64=None, token=None, *arg, **kwargs):
		form = self.get_form()

		assert uidb64 is not None and token is not None

		try:
			uid = urlsafe_base64_decode(uidb64)
			user = User._default_manager.get(pk=uid)
		except (TypeError, ValueError, OverflowError, User.DoesNotExist):
			user = None

		if user is not None and default_token_generator.check_token(user, token):
			if form.is_valid():
				new_password = form.cleaned_data['new_password']

				user.set_password(new_password)
				user.save()

				messages.success(request, _('Password reset successfully.'))

				return self.form_valid(form)
			else:
				messages.error(request, _('We were not able to reset your password.'))
				return self.form_invalid(form)
		else:
			messages.error(request, _('The reset password link is no longer valid.'))
			return self.form_invalid(form)

@log_decorator('user', 'access', 'system')
def login(request):
	context = {}
	context['title'] = _('Log In')
	security = Security.objects.get(id = 1)

	context['deny_register'] = security.allow_register

	if request.POST:
		username = request.POST['email']
		password = request.POST['password']
		user = authenticate(username=username, password=password)

		if user is not None:
			if not security.maintence or user.is_staff:
				login_user(request, user)

				users = User.objects.all().exclude(email = username)

				notification = {
					"type": "user_status",
					"user_id": str(user.id),
					"status": _u("Online"),
					"status_class": "active",
					"remove_class": "away"
				}

				notification = json.dumps(notification)

				for u in users:
					Group("user-%s" % u.id).send({'text': notification})

				next_url = request.GET.get('next', None)

				if next_url:
					return redirect(next_url)

				return redirect(reverse("home"))
			else:
				messages.error(request, _('System under maintenance. Try again later'))
		else:
			messages.error(request, _('E-mail or password are incorrect.'))
			context["username"] = username
	elif request.user.is_authenticated:
		return redirect(reverse('home'))

	return render(request, "users/login.html", context)

@log_decorator('user', 'logout', 'system')
def logout(request, next_page = None):
	user = request.user

	logout_user(request)

	users = User.objects.all().exclude(email = user.email)

	notification = {
		"type": "user_status",
		"user_id": str(user.id),
		"status": _u("Offline"),
		"status_class": "",
		"remove_class": "away"
	}

	notification = json.dumps(notification)

	for u in users:
		Group("user-%s" % u.id).send({'text': notification})

	if next_page:
		return redirect(next_page)

	return redirect(reverse('users:login'))






# API VIEWS
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	authentication_classes = [OAuth2Authentication]
	permissions_classes = (IsAuthenticatedOrTokenHasScope,)
