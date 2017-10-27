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

from amadeus.permissions import has_subject_permissions

from subjects.models import Subject

from log.mixins import LogMixin

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

class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = 'students_group'
	log_action = 'create'
	log_resource = 'students_group'
	log_context = {}

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

			self.log_action = 'replicate'

			self.log_context['replicated_group_id'] = group.id
			self.log_context['replicated_group_name'] = group.name
			self.log_context['replicated_group_slug'] = group.slug
		
		return initial

	def form_valid(self, form):
		self.object = form.save(commit = False)

		slug = self.kwargs.get('slug', '')
		subject = get_object_or_404(Subject, slug = slug)

		self.object.subject = subject

		self.object.save()

		self.log_context['category_id'] = self.object.subject.category.id
		self.log_context['category_name'] = self.object.subject.category.name
		self.log_context['category_slug'] = self.object.subject.category.slug
		self.log_context['subject_id'] = self.object.subject.id
		self.log_context['subject_name'] = self.object.subject.name
		self.log_context['subject_slug'] = self.object.subject.slug
		self.log_context['group_id'] = self.object.id
		self.log_context['group_name'] = self.object.name
		self.log_context['group_slug'] = self.object.slug

		super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return super(CreateView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)

		context['title'] = _('Create Group')

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

class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
	log_component = 'students_group'
	log_action = 'update'
	log_resource = 'students_group'
	log_context = {}

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

		self.log_context['category_id'] = self.object.subject.category.id
		self.log_context['category_name'] = self.object.subject.category.name
		self.log_context['category_slug'] = self.object.subject.category.slug
		self.log_context['subject_id'] = self.object.subject.id
		self.log_context['subject_name'] = self.object.subject.name
		self.log_context['subject_slug'] = self.object.subject.slug
		self.log_context['group_id'] = self.object.id
		self.log_context['group_name'] = self.object.name
		self.log_context['group_slug'] = self.object.slug

		super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('groups:index', kwargs = {'slug': self.object.subject.slug})

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = 'students_group'
	log_action = 'delete'
	log_resource = 'students_group'
	log_context = {}

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

		self.log_context['category_id'] = self.object.subject.category.id
		self.log_context['category_name'] = self.object.subject.category.name
		self.log_context['category_slug'] = self.object.subject.category.slug
		self.log_context['subject_id'] = self.object.subject.id
		self.log_context['subject_name'] = self.object.subject.name
		self.log_context['subject_slug'] = self.object.subject.slug
		self.log_context['group_id'] = self.object.id
		self.log_context['group_name'] = self.object.name
		self.log_context['group_slug'] = self.object.slug

		super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('groups:index', kwargs = {'slug': self.object.subject.slug})