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
from .forms import RegisterUserForm, ProfileForm

#API IMPORTS
from rest_framework import viewsets
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# ================ ADMIN =======================
# class UsersListView(HasRoleMixin, LoginRequiredMixin, generic.ListView):

# 	allowed_roles = ['system_admin']
# 	#login_url = reverse_lazy("core:home")
# 	redirect_field_name = 'next'
# 	template_name = 'list_users.html'
# 	context_object_name = 'users'
# 	paginate_by = 10

# 	def get_queryset(self):
# 		search = self.request.GET.get('search', None)

# 		if search is None:
# 			users = User.objects.all().order_by('name').exclude( username = self.request.user.username)
# 		else:
# 			users = User.objects.filter(Q(username = search) | Q(name = search) | Q(name__icontains = search) | Q(username__icontains = search)).exclude( username = self.request.user.username)

# 		return users

# 	def get_context_data (self, **kwargs):
# 		context = super(UsersListView, self).get_context_data(**kwargs)
# 		context['title'] = 'Manage Users'
# 		return context

# class Create(HasRoleMixin, LoginRequiredMixin, generic.edit.CreateView):

# 	allowed_roles = ['system_admin']
# 	#login_url = reverse_lazy("core:home")
# 	redirect_field_name = 'next'
# 	template_name = 'users/create.html'
# 	form_class = UserForm
# 	context_object_name = 'acc'
# 	success_url = reverse_lazy('users:manage')

# 	def form_valid(self, form):
# 		self.object = form.save()

# 		if self.object.type_profile == 2:
# 			assign_role(self.object, 'student')
# 		elif self.object.type_profile == 1:
# 			assign_role(self.object, 'professor')
# 		elif self.object.is_staff:
# 			assign_role(self.object, 'system_admin')

# 		self.object.save()

# 		messages.success(self.request, ('User ')+self.object.name+(' created successfully!'))

# 		return super(Create, self).form_valid(form)
# 	def get_context_data (self, **kwargs):
# 		context = super(Create, self).get_context_data(**kwargs)
# 		context['title'] = "Add User"
# 		return context

# class Update(HasRoleMixin, LoginRequiredMixin, generic.UpdateView):

# 	allowed_roles = ['system_admin']
# 	#login_url = reverse_lazy("core:home")
# 	redirect_field_name = 'next'
# 	template_name = 'users/update.html'
# 	slug_field = 'username'
# 	slug_url_kwarg = 'username'
# 	context_object_name = 'acc'
# 	model = User
# 	form_class = UserForm
# 	success_url = reverse_lazy('users:manage')

# 	def form_valid(self, form):
# 		self.object = form.save(commit = False)

# 		if self.object.type_profile == 2:
# 			assign_role(self.object, 'student')
# 		elif self.object.type_profile == 1:
# 			assign_role(self.object, 'professor')
# 		elif self.object.is_staff:
# 			assign_role(self.object, 'system_admin')

# 		self.object.save()

# 		messages.success(self.request, _('User ')+self.object.name+_(' updated successfully!'))

# 		return super(Update, self).form_valid(form)

# 	def get_context_data (self, **kwargs):
# 		context = super(Update, self).get_context_data(**kwargs)
# 		context['title'] = "Update User"
# 		return context

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
