from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from amadeus.permissions import has_subject_permissions

from subjects.models import Subject

from .models import StudentsGroup
from .forms import StudentsGroupForm

class IndexView(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	model = StudentsGroup
	context_object_name = 'groups'
	template_name = 'groups/index.html'
	paginate_by = 10

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		if not has_subject_permissions(request.user, subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(IndexView, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		return StudentsGroup.objects.filter(subject = subject)

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		context['title'] = _('Students Groups')
		context['subject'] = subject

		return context

class CreateView(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'groups/create.html'
	form_class = StudentsGroupForm

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		if not has_subject_permissions(request.user, subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(CreateView, self).dispatch(request, *args, **kwargs)

	def get_initial(self):
		initial = super(CreateView, self).get_initial()

		slug = self.kwargs.get('slug', '')

		initial['subject'] = get_object_or_404(Subject, slug = slug)

		if self.kwargs.get('group_slug'):
			group = get_object_or_404(StudentsGroup, slug = self.kwargs['group_slug'])
			initial = initial.copy()
			initial['description'] = group.description
			initial['name'] = group.name
			initial['participants'] = group.participants.all()
		
		return initial

	def form_valid(self, form):
		self.object = form.save(commit = False)

		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		self.object.subject = subject

		self.object.save()

		return super(CreateView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)

		context['title'] = _('Create Topic')

		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		context['subject'] = subject

		if self.kwargs.get('group_slug'):
			group = get_object_or_404(StudentsGroup, slug = self.kwargs['group_slug'])

			context['title'] = _('Replicate Group')

			context['group'] = group

		return context

	def get_success_url(self):
		messages.success(self.request, _('The group "%s" was created successfully!')%(self.object.name))

		return reverse_lazy('groups:index', kwargs = {'slug': self.object.subject.slug})

class UpdateView(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'groups/update.html'
	model = StudentsGroup
	form_class = StudentsGroupForm
	context_object_name = 'group'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('sub_slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		if not has_subject_permissions(request.user, subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(UpdateView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)

		context['title'] = _('Update Group')

		slug = self.kwargs.get('sub_slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		context['subject'] = subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('The group "%s" was updated successfully!')%(self.object.name))

		return reverse_lazy('groups:index', kwargs = {'slug': self.object.subject.slug})

class DeleteView(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'groups/delete.html'
	model = StudentsGroup
	context_object_name = 'group'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		group = get_object_or_404(StudentsGroup, slug = slug)

		if not has_subject_permissions(request.user, group.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(DeleteView, self).dispatch(request, *args, **kwargs)

	def get_success_url(self):
		messages.success(self.request, _('The group "%s" was removed successfully!')%(self.object.name))

		return reverse_lazy('groups:index', kwargs = {'slug': self.object.subject.slug})