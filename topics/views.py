from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

import json

from amadeus.permissions import has_subject_permissions

from subjects.models import Subject

from .models import Topic, Resource
from .forms import TopicForm

class CreateView(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'topics/create.html'
	form_class = TopicForm

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
		
		return initial

	def form_valid(self, form):
		self.object = form.save(commit = False)

		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		self.object.subject = subject
		self.object.order = subject.topic_subject.count() + 1

		self.object.save()

		return super(CreateView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)

		context['title'] = _('Create Topic')

		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		context['subject'] = subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('Topic "%s" was created on virtual enviroment "%s" successfully!')%(self.object.name, self.object.subject.name))

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.subject.slug})

class UpdateView(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'topics/update.html'
	form_class = TopicForm
	model = Topic
	context_object_name = 'topic'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('sub_slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		if not has_subject_permissions(request.user, subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(UpdateView, self).dispatch(request, *args, **kwargs)

	def get_initial(self):
		initial = super(UpdateView, self).get_initial()

		slug = self.kwargs.get('sub_slug', '')

		initial['subject'] = get_object_or_404(Subject, slug = slug)
		
		return initial

	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)

		context['title'] = _('Update Topic')

		slug = self.kwargs.get('sub_slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		context['subject'] = subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('Topic "%s" was updated on virtual enviroment "%s" successfully!')%(self.object.name, self.object.subject.name))

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.subject.slug})

class DeleteView(LoginRequiredMixin, generic.DeleteView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'topics/delete.html'
	model = Topic
	context_object_name = 'topic'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		if not has_subject_permissions(request.user, topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(DeleteView, self).dispatch(request, *args, **kwargs)

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()

		if self.object.resource_topic.count() > 0:
			messages.error(self.request, _('Could not remove this topic. It has on or more resources attached.'))

			return redirect(reverse_lazy('subjects:view', kwargs = {'slug': self.object.subject.slug}))
		else:
			self.object.delete()

		return redirect(self.get_success_url())

	def get_success_url(self):
		messages.success(self.request, _('Topic "%s" was removed from virtual enviroment "%s" successfully!')%(self.object.name, self.object.subject.name))

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.subject.slug})

def update_order(request):
	data = request.GET.get('data', None)

	if not data is None:
		data = json.loads(data)

		for t_data in data:
			topic = get_object_or_404(Topic, id = t_data['topic_id'])
			topic.order = t_data['topic_order']
			topic.save()

		return JsonResponse({'message': 'ok'})

	return JsonResponse({'message': 'No data received'})

def update_resource_order(request):
	data = request.GET.get('data', None)

	if not data is None:
		data = json.loads(data)

		for t_data in data:
			resource = get_object_or_404(Resource, id = t_data['resource_id'])
			resource.order = t_data['resource_order']
			resource.save()

		return JsonResponse({'message': 'ok'})

	return JsonResponse({'message': 'No data received'})