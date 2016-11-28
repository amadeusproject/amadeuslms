from django.shortcuts import get_object_or_404,redirect
from django.db.models import Q
from django.views import generic
from django.contrib import messages
from rolepermissions.mixins import HasRoleMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from rolepermissions.shortcuts import assign_role
from rolepermissions.verifications import has_role
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import User
from .forms import UserForm, UpdateProfileForm, UpdateUserForm, UpdateProfileFormAdmin
from links.models import Link
from poll.models import *
from forum.models import *
from files.models import *
from exam.models import *
from courses.models import *

#API IMPORTS
from rest_framework import viewsets
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# ================ ADMIN =======================
class UsersListView(HasRoleMixin, LoginRequiredMixin, generic.ListView):

	allowed_roles = ['system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'list_users.html'
	context_object_name = 'users'
	paginate_by = 10

	def get_queryset(self):
		search = self.request.GET.get('search', None)

		if search is None:
			users = User.objects.all().order_by('name').exclude( username = self.request.user.username)
		else:
			users = User.objects.filter(Q(username = search) | Q(name = search) | Q(name__icontains = search) | Q(username__icontains = search)).exclude( username = self.request.user.username)

		return users

	def get_context_data (self, **kwargs):
		context = super(UsersListView, self).get_context_data(**kwargs)
		context['title'] = 'Manage Users | Amadeus'
		return context

class Create(HasRoleMixin, LoginRequiredMixin, generic.edit.CreateView):

	allowed_roles = ['system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'users/create.html'
	form_class = UserForm
	context_object_name = 'acc'
	success_url = reverse_lazy('users:manage')

	def form_valid(self, form):
		self.object = form.save()

		if self.object.type_profile == 2:
			assign_role(self.object, 'student')
		elif self.object.type_profile == 1:
			assign_role(self.object, 'professor')
		elif self.object.is_staff:
			assign_role(self.object, 'system_admin')

		self.object.save()

		messages.success(self.request, ('User ')+self.object.name+(' created successfully!'))

		return super(Create, self).form_valid(form)
	def get_context_data (self, **kwargs):
		context = super(Create, self).get_context_data(**kwargs)
		context['title'] = "Add User | Amadeus"
		return context

class Update(HasRoleMixin, LoginRequiredMixin, generic.UpdateView):

	allowed_roles = ['system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'users/update.html'
	slug_field = 'username'
	slug_url_kwarg = 'username'
	context_object_name = 'acc'
	model = User
	form_class = UpdateUserForm
	success_url = reverse_lazy('users:manage')

	def form_valid(self, form):
		self.object = form.save(commit = False)

		if self.object.type_profile == 2:
			assign_role(self.object, 'student')
		elif self.object.type_profile == 1:
			assign_role(self.object, 'professor')
		elif self.object.is_staff:
			assign_role(self.object, 'system_admin')

		self.object.save()

		messages.success(self.request, _('User ')+self.object.name+_(' updated successfully!'))

		return super(Update, self).form_valid(form)

	def get_context_data (self, **kwargs):
		context = super(Update, self).get_context_data(**kwargs)
		context['title'] = "Update User | Amadeus"
		return context

class View(LoginRequiredMixin, generic.DetailView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = User
	context_object_name = 'acc'
	template_name = 'users/view.html'
	slug_field = 'username'
	slug_url_kwarg = 'username'

	def get_context_data (self, **kwargs):
		context = super(View, self).get_context_data(**kwargs)
		context['title'] = "User | Amadeus"
		return context

def delete_user(request,username):
	user = get_object_or_404(User,username = username)
	user.delete()
	messages.success(request,_("User deleted Successfully!"))
	return redirect('users:manage')

def remove_account(request,username):
	user = get_object_or_404(User,username = username)
	user.delete()
	messages.success(request,_("User deleted Successfully!"))
	return redirect('core:logout')

class Change_password(generic.TemplateView):
	template_name = 'users/change_password.html'

	def get_context_data (self, **kwargs):
		context = super(Change_password, self).get_context_data(**kwargs)
		context['title'] = "Change Password | Amadeus"
		return context

class Remove_account(generic.TemplateView):
	template_name = 'users/remove_account.html'

	def get_context_data (self, **kwargs):
		context = super(Remove_account, self).get_context_data(**kwargs)
		context['title'] = "Remove Account | Amadeus"
		return context

class UpdateProfile(LoginRequiredMixin, generic.edit.UpdateView):
	login_url = reverse_lazy("core:home")
	template_name = 'users/edit_profile.html'
	form_class = UpdateProfileForm
	success_url = reverse_lazy('users:profile')

	def get_object(self):
		user = get_object_or_404(User, username = self.request.user.username)
		return user

	def get_context_data(self, **kwargs):
		context = super(UpdateProfile, self).get_context_data(**kwargs)
		context['title'] = 'Update Profile | Amadeus'
		if has_role(self.request.user, 'system_admin'):
			context['form'] = UpdateProfileFormAdmin(instance = self.object)
		else:
			context['form'] = UpdateProfileForm(instance = self.object)
		return context

	def form_valid(self, form):
		form.save()
		messages.success(self.request, _('Profile edited successfully!'))

		return super(UpdateProfile, self).form_valid(form)

class DeleteUser(LoginRequiredMixin, generic.edit.DeleteView):
	allowed_roles = ['student']
	login_url = reverse_lazy("core:home")
	model = User
	success_url = reverse_lazy('core:index')
	success_message = "Deleted Successfully"

	def get_queryset(self):
		user = get_object_or_404(User, username = self.request.user.username)
		return user


class Profile(LoginRequiredMixin, generic.DetailView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	context_object_name = 'user'
	template_name = 'users/profile.html'

	def get_object(self):
		user = get_object_or_404(User, username = self.request.user.username)
		return user

	def get_context_data (self, **kwargs):
		context = super(Profile, self).get_context_data(**kwargs)
		context['title'] = "Profile | Amadeus"
		return context

class SearchView(LoginRequiredMixin, generic.ListView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	queryset = Material.objects.all()
	template_name = 'users/search.html'
	paginate_by = 10

	def get_context_data(self, **kwargs):
		context = super(SearchView, self).get_context_data(**kwargs)
		search = self.request.GET.get('search', None)
		link_list = []
		file_list = []
		poll_list = []
		exam_list = []
		forum_list = []
		qtd = 0

		if has_role(self.request.user,'system_admin'):
			if search != '':
				link_list = Link.objects.filter( Q(name__icontains=search)).order_by('name')
				file_list = TopicFile.objects.filter(Q(name__icontains=search)).order_by('name')
				poll_list = Poll.objects.filter(Q(name__icontains=search)).order_by('name')
				exam_list = Exam.objects.filter(Q(name__icontains=search)).order_by('name')
				forum_list = Forum.objects.filter(Q(name__icontains=search)).order_by('name')
				qtd = len(link_list) + len(file_list) + len(poll_list) + len(exam_list) + len(forum_list)

		elif has_role(self.request.user,'professor'):
			topics = Topic.objects.filter(owner = self.request.user)
			links = Link.objects.all()
			files = TopicFile.objects.all()
			polls = Poll.objects.all()
			exams = Exam.objects.all()
			forums = Forum.objects.all()
			if search != '':
				link_list = sorted([link for link in links for topic in topics if (link.topic == topic) and ( search in link.name ) ],key = lambda x:x.name)
				exam_list = sorted([exam for exam in exams for topic in topics if (exam.topic == topic) and ( search in exam.name ) ],key = lambda x:x.name)
				file_list = sorted([arquivo for arquivo in files for topic in topics if (arquivo.topic == topic) and  (search in arquivo.name ) ],key = lambda x:x.name)
				poll_list = sorted([poll for poll in polls for topic in topics if (poll.topic == topic) and ( search in poll.name ) ],key = lambda x:x.name)
				forum_list = sorted([forum for forum in forums for topic in topics if (forum.topic == topic) and ( search in forum.name ) ],key = lambda x:x.name)
				qtd = len(link_list) + len(file_list) + len(poll_list) + len(exam_list) + len(forum_list)

		elif has_role(self.request.user, 'student'):
			if search != '':
				link_list = Link.objects.filter( Q(name__icontains=search) and Q(students__name = self.request.user.name)).order_by('name')
				file_list = TopicFile.objects.filter(Q(name__icontains=search) and Q(students__name = self.request.user.name)).order_by('name')
				poll_list = Poll.objects.filter(Q(name__icontains=search)and Q(students__name = self.request.user.name)).order_by('name')
				exam_list = Exam.objects.filter(Q(name__icontains=search)and Q(students__name = self.request.user.name)).order_by('name')
				forum_list = Forum.objects.filter(Q(name__icontains=search)and Q(students__name = self.request.user.name)).order_by('name')
				qtd = len(link_list) + len(file_list) + len(poll_list) + len(exam_list) + len(forum_list)


		context['link_list'] = link_list
		context['file_list'] = file_list
		context['poll_list'] = poll_list
		context['exam_list'] = exam_list
		context['forum_list'] = forum_list
		context['qtd'] = qtd

		return context


# API VIEWS

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permissions_classes = (IsAuthenticatedOrReadOnly,)
