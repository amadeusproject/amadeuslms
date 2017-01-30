from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from datetime import datetime

from amadeus.permissions import has_subject_view_permissions

from subjects.models import Subject

from .models import Notification

class SubjectNotifications(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	context_object_name = 'notifications'
	template_name = 'notifications/subject.html'
	paginate_by = 10
	total = 0

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		if not has_subject_view_permissions(request.user, subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(SubjectNotifications, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject, creation_date = datetime.now())

		self.total = notifications.count()

		return notifications

	def get_context_data(self, **kwargs):
		context = super(SubjectNotifications, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		context['title'] = _('%s - Pendencies')%(subject.name)
		context['subject'] = subject
		context['total'] = self.total

		return context

class SubjectHistory(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	context_object_name = 'notifications'
	template_name = 'notifications/subject.html'
	paginate_by = 10
	total = 0
	num_rows = 0

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		if not has_subject_view_permissions(request.user, subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(SubjectHistory, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject).order_by("-creation_date")

		self.total = notifications.filter(creation_date = datetime.now()).count()
		self.num_rows = notifications.count()

		return notifications

	def get_context_data(self, **kwargs):
		context = super(SubjectHistory, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		context['title'] = _('%s - Pendencies')%(subject.name)
		context['subject'] = subject
		context['history'] = True
		context['total'] = self.total
		context['rows'] = self.num_rows

		return context