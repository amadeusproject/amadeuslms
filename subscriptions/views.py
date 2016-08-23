from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from rolepermissions.mixins import HasRoleMixin
from .forms import SubscribeForm
from .models import Subscribe
from courses.models import Course

@login_required
def subscribe(request):
	if request.method == 'POST':
		print(request.POST)
		form = SubscribeForm(request.POST)

		print(form)

		if form.is_valid():
			form.save()

			messages.success(request, _('Course subscribed successfully!'))

			return redirect('app:course:manage')

class Index(HasRoleMixin, LoginRequiredMixin, generic.ListView):

	allowed_roles = ['student']
	login_url = '/'
	redirect_field_name = 'next'
	template_name = 'subscribed/index.html'
	context_object_name = 'subscriptions'
	paginate_by = 10

	def get_queryset(self):
		return Subscribe.objects.filter(user = self.request.user)

class Participants(HasRoleMixin, LoginRequiredMixin, generic.ListView):

	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	template_name = 'subscribed/participants.html'
	context_object_name = 'subscribers'
	paginate_by = 10

	def get_queryset(self):
		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))
		return Subscribe.objects.filter(course = course)