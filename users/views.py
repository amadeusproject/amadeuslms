from django.http import Http404
from django.shortcuts import get_object_or_404,redirect, render
from django.db.models import Q
from django.views import generic
from django.contrib import messages
from rolepermissions.mixins import HasRoleMixin
from django.contrib.auth import authenticate, login as login_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from rolepermissions.shortcuts import assign_role
from rolepermissions.verifications import has_role
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import User
from .forms import RegisterUserForm, ProfileForm, UserForm

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

class Profile(LoginRequiredMixin, generic.DetailView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	context_object_name = 'acc'
	template_name = 'users/profile.html'

	def get_object(self):
		user = get_object_or_404(User, username = self.request.user.username)

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
		
		assign_role(form.instance, 'student')

		messages.success(self.request, _('User successfully registered!'))

		return super(RegisterUser, self).form_valid(form)

def login(request):
	context = {}
	context['title'] = _('Log In')

	if request.POST:
		username = request.POST['email']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login_user(request, user)
			return redirect(reverse("users:login"))
		else:
			messages.add_message(request, messages.ERROR, _('E-mail or password are incorrect.'))
			context["username"] = username
	elif request.user.is_authenticated:
		return redirect('home')

	return render(request,"users/login.html",context)


# API VIEWS
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permissions_classes = (IsAuthenticatedOrReadOnly,)
