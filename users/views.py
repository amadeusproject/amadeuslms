from django.shortcuts import get_object_or_404,redirect, render
from django.views import generic
from django.contrib import messages
from rolepermissions.mixins import HasRoleMixin
from django.contrib.auth import authenticate, login as login_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from rolepermissions.shortcuts import assign_role
from rolepermissions.verifications import has_role

from .models import User
from .forms import RegisterUserForm, ProfileForm, UserForm, ChangePassForm, PassResetRequest, SetPasswordForm

#RECOVER PASS IMPORTS
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader

#API IMPORTS
from rest_framework import viewsets
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# ================ ADMIN =======================

# class View(LoginRequiredMixin, generic.DetailView):

# 	#login_url = reverse_lazy("core:home")
# 	redirect_field_name = 'next'
# 	model = User
# 	context_object_name = 'acc'
# 	template_name = 'users/view.html'
# 	slug_field = 'username'
# 	slug_url_kwarg = 'username'

# 	def get_context_data (self, **kwargs):
# 		context = super(View, self).get_context_data(**kwargs)
# 		context['title'] = "User"
# 		return context

# def delete_user(request,username):
# 	user = get_object_or_404(User,username = username)
# 	user.delete()
# 	messages.success(request,_("User deleted Successfully!"))
# 	return redirect('users:manage')

# def remove_account(request,username):
# 	user = get_object_or_404(User,username = username)
# 	user.delete()
# 	messages.success(request,_("User deleted Successfully!"))
# 	#return redirect('core:logout')

# class Change_password(generic.TemplateView):
# 	template_name = 'users/change_password.html'

# 	def get_context_data (self, **kwargs):
# 		context = super(Change_password, self).get_context_data(**kwargs)
# 		context['title'] = "Change Password"
# 		return context

# class Remove_account(generic.TemplateView):
# 	template_name = 'users/remove_account.html'

# 	def get_context_data (self, **kwargs):
# 		context = super(Remove_account, self).get_context_data(**kwargs)
# 		context['title'] = "Remove Account"
# 		return context



# class DeleteUser(LoginRequiredMixin, generic.edit.DeleteView):
# 	allowed_roles = ['student']
# 	#login_url = reverse_lazy("core:home")
# 	model = User
	
# 	#success_url = reverse_lazy('core:index')
# 	success_message = "Deleted Successfully"

# 	def get_queryset(self):
# 		user = get_object_or_404(User, username = self.request.user.username)
# 		return user

# class SearchView(LoginRequiredMixin, generic.ListView):

# 	#login_url = reverse_lazy("core:home")
# 	redirect_field_name = 'next'
# 	queryset = None
# 	template_name = 'users/search.html'
# 	paginate_by = 10

# 	def get_context_data(self, **kwargs):
# 		context = super(SearchView, self).get_context_data(**kwargs)
# 		search = self.request.GET.get('search', None)
		

# 		return context

class UsersListView(LoginRequiredMixin, generic.ListView):
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

		return context

class CreateView(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'users/create.html'
	form_class = UserForm
	context_object_name = 'acc'
	success_url = reverse_lazy('users:manage')

	def form_valid(self, form):
		self.object = form.save()

		msg = _("User %s created successfully" % self.object.get_short_name())

		messages.success(self.request, msg)

		return super(CreateView, self).form_valid(form)

	def get_context_data (self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)
		context['title'] = _("Add User")

		return context

class UpdateView(LoginRequiredMixin, generic.UpdateView):
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

		msg = _("User %s updated successfully" % self.object.get_short_name())

		messages.success(self.request, msg)

		return super(UpdateView, self).form_valid(form)

	def get_context_data (self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)
		context['title'] = _("Update User")

		return context

class DeleteView(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'users/delete.html'
	model = User
	slug_url_kwarg = 'email'
	context_object_name = 'acc'

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
			success_url = reverse_lazy('users:login')
			error_url = reverse_lazy('users:profile')
		else:
			success_url = reverse_lazy('users:manage')
			error_url = reverse_lazy('users:manage')

		success_msg = _('User removed successfully!')
		error_msg = _('Could not remove the account. The user is attach to one or more functions (administrator, coordinator, professor ou student) in the system.')

		if user.has_dependencies():
			messages.error(self.request, error_msg)

			return redirect(error_url)
		else:
			user.delete()
			
			messages.success(self.request, success_msg)

			return redirect(success_url)

	def get_context_data(self, **kwargs):
		context = super(DeleteView, self).get_context_data(**kwargs)
		context['title'] = _('Delete Account')

		return context

	def render_to_response(self, context, **response_kwargs):
		email = self.kwargs.get('email', None)

		if email is None:
			template = 'users/delete_account.html'
		else:
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

					subject_template_name='registration/password_reset_subject.txt'
					email_template_name = 'recover_pass_email_template.html'
					
					subject = loader.render_to_string(subject_template_name, c)
	                # Email subject *must not* contain newlines
					subject = ''.join(subject.splitlines())
					email = loader.render_to_string(email_template_name, c)
					
					send_mail(subject, email, settings.DEFAULT_FROM_EMAIL , [user.email], fail_silently=False)

				result = self.form_valid(form)
				messages.success(request, _("Soon you'll receive an email with instructions to set your new password. If you don't receive it in 24 hours, please check your spam box."))
				
				return result
		
		result = self.form_invalid(form)
		messages.error(request, _('No user is associated with this email address'))
		
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


def login(request):
	context = {}
	context['title'] = _('Log In')

	if request.POST:
		username = request.POST['email']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login_user(request, user)
			return redirect(reverse("home"))
		else:
			messages.error(request, _('E-mail or password are incorrect.'))
			context["username"] = username
	elif request.user.is_authenticated:
		return redirect(reverse('home'))

	return render(request,"users/login.html",context)


# API VIEWS
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permissions_classes = (IsAuthenticatedOrReadOnly,)
