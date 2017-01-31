from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count

from dateutil import parser
from datetime import datetime
from django.utils import formats, timezone

from amadeus.permissions import has_subject_view_permissions

from subjects.models import Subject

from .models import Notification
from .utils import get_order_by, is_date

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

		notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject, creation_date = datetime.now()).order_by("task__limit_date", "task__end_date")

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

		order = get_order_by(self.request.GET.get("order_by", None))
		search = self.request.GET.get("search", None)

		notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject).order_by(*order)

		self.total = notifications.filter(creation_date = datetime.now()).count()
		
		if search:
			queries = Q(task__resource__name__icontains = search)
			queries |= Q(task__action__icontains = search)

			if search.isdigit():
				queries |= Q(level = search)

			if is_date(search):
				search_date = parser.parse(search)
				search_date = timezone.make_aware(search_date, timezone.get_current_timezone())

				queries |= Q(creation_date = search_date)
				queries |= Q(task__limit_date = search_date)
				queries |= Q(task__end_date = search_date)
				queries |= Q(meta__date = search_date)

			notifications = notifications.filter(queries).order_by(*order)

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
		context['searched'] = self.request.GET.get("search", "")

		return context

class IndexView(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	context_object_name = 'notifications'
	template_name = 'notifications/index.html'
	paginate_by = 10

	def get_queryset(self):
		notifications = Notification.objects.filter(user = self.request.user, viewed = False, creation_date = datetime.now()).values('task__resource__topic__subject', 'task__resource__topic__subject__name').annotate(total = Count('task__resource__topic__subject'))

		return notifications

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)

		context['title'] = _('Pendencies')

		return context

class AjaxNotifications(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	context_object_name = 'notifications'
	template_name = 'notifications/_view.html'

	def get_queryset(self):
		subject_id = self.kwargs.get('id', '')
		
		notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject__id = subject_id, creation_date = datetime.now()).order_by("task__limit_date", "task__end_date")

		return notifications

class AjaxHistory(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	context_object_name = 'notifications'
	template_name = 'notifications/_ajax_history.html'

	def get_queryset(self):
		subject_id = self.kwargs.get('id', '')

		order = get_order_by(self.request.GET.get("order_by", None))
		search = self.request.GET.get("search", None)

		notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject__id = subject_id).order_by(*order)

		if search:
			queries = Q(task__resource__name__icontains = search)
			queries |= Q(task__action__icontains = search)

			if search.isdigit():
				queries |= Q(level = search)

			if is_date(search):
				search_date = parser.parse(search)
				search_date = timezone.make_aware(search_date, timezone.get_current_timezone())

				queries |= Q(creation_date = search_date)
				queries |= Q(task__limit_date = search_date)
				queries |= Q(task__end_date = search_date)
				queries |= Q(meta__date = search_date)

			notifications = notifications.filter(queries).order_by(*order)

		self.num_rows = notifications.count()

		return notifications

	def get_context_data(self, **kwargs):
		context = super(AjaxHistory, self).get_context_data(**kwargs)

		subject_id = self.kwargs.get('id', '')

		context['subject_id'] = subject_id
		context['rows'] = self.num_rows
		context['searched'] = self.request.GET.get("search", "")
		context['order_by'] = self.request.GET.get("order_by", "")

		return context

@login_required
def set_goal(request):
	if request.method == "POST" and request.is_ajax():
		meta = request.POST.get('meta', None)

		if not meta:
			return JsonResponse({'error': True, 'message': _('No goal date received')})

		meta = parser.parse(meta)

		notify_id = request.POST.get('id', None)

		if not notify_id:
			return JsonResponse({'error': True, 'message': _('Could not identify the notification')})

		notification = get_object_or_404(Notification, id = notify_id)

		meta = timezone.make_aware(meta, timezone.get_current_timezone())

		if meta < timezone.now():
			return JsonResponse({'error': True, 'message': _("The goal date should be equal or after today's date")})

		if meta.date() > notification.task.resource.topic.subject.end_date:
			return JsonResponse({'error': True, 'message': _("The goal date should be equal or before subject's date")})

		notification.meta = meta
		notification.save()

		if notification.level == 2:
			message = _('Your new goal to realize the task %s is %s')%(str(notification.task), formats.date_format(meta, "SHORT_DATETIME_FORMAT"))
		else:
			message = _('Your goal to realize the task %s is %s')%(str(notification.task), formats.date_format(meta, "SHORT_DATETIME_FORMAT"))

	return JsonResponse({'error': False, 'message': message})