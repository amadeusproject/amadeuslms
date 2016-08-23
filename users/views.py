from django.shortcuts import render, get_object_or_404, redirect
from rolepermissions.shortcuts import assign_role
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from .models import User
from .forms import UserForm, ProfileForm

@login_required
def index(request):
	context = {
		'users': User.objects.exclude(username = request.user.username)
	}

	return render(request, "users/index.html", context)

@login_required
def create(request):
	context = {}

	form = UserForm(request.POST or None, request.FILES or None)
	
	if form.is_valid():
		user = form.save(commit = False)

		if user.type_profile == 2:
			assign_role(user, 'student')
		elif user.type_profile == 1:
			assign_role(user, 'professor')
		elif user.is_staff:
			assign_role(user, 'system_admin')

		user.save()

		messages.success(request, _('User created successfully!'))

		return redirect('app:users:manage')
	
	context['form'] = form

	return render(request, "users/create.html", context)

@login_required
def update(request, login):
	context = {}

	user = get_object_or_404(User, username = login)

	form = UserForm(request.POST or None, request.FILES or None, instance = user)
	
	if form.is_valid():
		new_user = form.save(commit = False)

		if user.type_profile == 2:
			assign_role(user, 'student')
		elif user.type_profile == 1:
			assign_role(user, 'professor')
		elif user.is_staff:
			assign_role(user, 'system_admin')

		new_user.save()

		messages.success(request, _('User edited successfully!'))

		return redirect('app:users:manage')
	
	context['form'] = form

	return render(request, "users/update.html", context)

@login_required
def view(request, login):
	context = {}

	user = get_object_or_404(User, username = login)

	context['acc'] = user

	return render(request, "users/view.html", context)

@login_required
def profile(request):
	context = {
		'user': request.user
	}

	return render(request, "users/profile.html", context)

@login_required
def edit_profile(request):
	form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    
	context = {}
    
	if form.is_valid():
		user = form.save(commit = False)

		if user.type_profile == 2:
			assign_role(user, 'student')
		elif user.type_profile == 1:
			assign_role(user, 'professor')
		elif user.is_staff:
			assign_role(user, 'system_admin')

		user.save()

		messages.success(request, _('Profile edited successfully!'))

	context['form'] = form

	return render(request, "users/edit_profile.html", context)