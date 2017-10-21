""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

import json
import time

from log.models import Log
from log.mixins import LogMixin
from log.decorators import log_decorator_ajax

from amadeus.permissions import has_subject_permissions

from subjects.models import Subject

from .models import Topic, Resource
from .forms import TopicForm


class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = 'topic'
	log_action = 'create'
	log_resource = 'topic'
	log_context = {}

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

		if not self.object.subject.visible and not self.object.repository:
			self.object.visible = False
			self.object.save()

		self.log_context['category_id'] = self.object.subject.category.id
		self.log_context['category_name'] = self.object.subject.category.name
		self.log_context['category_slug'] = self.object.subject.category.slug
		self.log_context['subject_id'] = self.object.subject.id
		self.log_context['subject_name'] = self.object.subject.name
		self.log_context['subject_slug'] = self.object.subject.slug
		self.log_context['topic_id'] = self.object.id
		self.log_context['topic_name'] = self.object.name
		self.log_context['topic_slug'] = self.object.slug

		super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

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

class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
	log_component = 'topic'
	log_action = 'update'
	log_resource = 'topic'
	log_context = {}

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
		if not self.object.subject.visible:
			self.object.visible = False
			self.object.save()

		if not self.object.visible and not self.object.repository:
			Resource.objects.filter(topic = self.object).update(visible = False)

		messages.success(self.request, _('Topic "%s" was updated on virtual enviroment "%s" successfully!')%(self.object.name, self.object.subject.name))

		self.log_context['category_id'] = self.object.subject.category.id
		self.log_context['category_name'] = self.object.subject.category.name
		self.log_context['category_slug'] = self.object.subject.category.slug
		self.log_context['subject_id'] = self.object.subject.id
		self.log_context['subject_name'] = self.object.subject.name
		self.log_context['subject_slug'] = self.object.subject.slug
		self.log_context['topic_id'] = self.object.id
		self.log_context['topic_name'] = self.object.name
		self.log_context['topic_slug'] = self.object.slug

		super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.subject.slug})

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = 'topic'
	log_action = 'delete'
	log_resource = 'topic'
	log_context = {}

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
			messages.error(self.request, _('Could not remove this topic. It has one or more resources attached.'))

			return redirect(reverse_lazy('subjects:view', kwargs = {'slug': self.object.subject.slug}))
		else:
			self.object.delete()

		return redirect(self.get_success_url())

	def get_success_url(self):
		messages.success(self.request, _('Topic "%s" was removed from virtual enviroment "%s" successfully!')%(self.object.name, self.object.subject.name))

		self.log_context['category_id'] = self.object.subject.category.id
		self.log_context['category_name'] = self.object.subject.category.name
		self.log_context['category_slug'] = self.object.subject.category.slug
		self.log_context['subject_id'] = self.object.subject.id
		self.log_context['subject_name'] = self.object.subject.name
		self.log_context['subject_slug'] = self.object.subject.slug
		self.log_context['topic_id'] = self.object.id
		self.log_context['topic_name'] = self.object.name
		self.log_context['topic_slug'] = self.object.slug

		super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.subject.slug})

@log_decorator_ajax('topic', 'view', 'topic')
def topic_view_log(request, topic):
	action = request.GET.get('action')

	if action == 'open':
		topic = get_object_or_404(Topic, id = topic)

		log_context = {}
		log_context['category_id'] = topic.subject.category.id
		log_context['category_name'] = topic.subject.category.name
		log_context['category_slug'] = topic.subject.category.slug
		log_context['subject_id'] = topic.subject.id
		log_context['subject_name'] = topic.subject.name
		log_context['subject_slug'] = topic.subject.slug
		log_context['topic_id'] = topic.id
		log_context['topic_name'] = topic.name
		log_context['topic_slug'] = topic.slug
		log_context['timestamp_start'] = str(int(time.time()))
		log_context['timestamp_end'] = '-1'

		request.log_context = log_context

		log_id = Log.objects.latest('id').id

		return JsonResponse({'message': 'ok', 'log_id': log_id})

	return JsonResponse({'message': 'ok'})

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


