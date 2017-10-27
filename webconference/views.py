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
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from webpage.forms import FormModalMessage
from chat.models import Conversation, TalkMessages, ChatVisualizations
import textwrap
import json
from django.db.models import Q
from channels import Group
import datetime
from users.models import User
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.utils import formats
from subjects.models import Subject

from amadeus.permissions import has_subject_permissions, has_resource_permissions

import time
from log.models import Log
from log.mixins import LogMixin
from log.decorators import log_decorator

from topics.models import Topic

from braces import views as braces_mixins

from .forms import WebconferenceForm, SettingsForm, InlinePendenciesFormset, WebConferenceUpdateForm
from .models import Webconference, ConferenceSettings as Settings

class NewWindowView(LoginRequiredMixin,LogMixin, generic.DetailView):
	log_component = 'resources'
	log_action = 'view'
	log_resource = 'webconference'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webconference/window_view.html'
	model = Webconference
	context_object_name = 'webconference'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webconference = get_object_or_404(Webconference, slug = slug)

		if not has_resource_permissions(request.user, webconference):
			return redirect(reverse_lazy('subjects:home'))

		return super(NewWindowView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(NewWindowView, self).get_context_data(**kwargs)
		context['title'] = _("%s - Web Conference")%(self.object.name)
		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['webconference_id'] = self.object.id
		self.log_context['webconference_name'] = self.object.name
		self.log_context['webconference_slug'] = self.object.slug
		self.log_context['webconference_view'] = str(int(time.time()))

		super(NewWindowView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['log_id'] = Log.objects.latest('id').id

		return context

class Conference(LoginRequiredMixin,LogMixin,generic.TemplateView):

	log_component = 'resources'
	log_action = 'initwebconference'
	log_resource = 'webconference'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webconference/jitsi.html'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		conference = get_object_or_404(Webconference, slug = slug)

		if not has_resource_permissions(request.user, conference):
			return redirect(reverse_lazy('subjects:home'))

		return super(Conference, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(Conference, self).get_context_data(**kwargs)
		conference = get_object_or_404(Webconference, slug = kwargs.get('slug'))
		context['title'] = _("%s - Web Conference")%(conference)
		context['webconference'] = conference
		context['topic'] = conference.topic
		context['subject'] = conference.topic.subject
		context['name_room'] = kwargs.get('slug')
		

		context['user_image'] = self.request.build_absolute_uri(str(self.request.user.image_url))

		try:
			context['domain'] = Settings.objects.last().domain
		except AttributeError:
			context['domain'] = 'meet.jit.si'


		self.log_context['category_id'] = conference.topic.subject.category.id
		self.log_context['category_name'] = conference.topic.subject.category.name
		self.log_context['category_slug'] = conference.topic.subject.category.slug
		self.log_context['subject_id'] = conference.topic.subject.id
		self.log_context['subject_name'] = conference.topic.subject.name
		self.log_context['subject_slug'] = conference.topic.subject.slug
		self.log_context['topic_id'] = conference.topic.id
		self.log_context['topic_name'] = conference.topic.name
		self.log_context['topic_slug'] = conference.topic.slug
		self.log_context['webconference_id'] = conference.id
		self.log_context['webconference_name'] = conference.name
		self.log_context['webconference_slug'] = conference.slug
		self.log_context['webconference_init'] = str(int(time.time()))

		super(Conference, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return context

@log_decorator('resources', 'participating', 'webconference')
def participating(request):
	webconference = get_object_or_404(Webconference, slug = request.GET['slug'])
	log_context = {}
	log_context['category_id'] = webconference.topic.subject.category.id
	log_context['category_name'] = webconference.topic.subject.category.name
	log_context['category_slug'] = webconference.topic.subject.category.slug
	log_context['subject_id'] = webconference.topic.subject.id
	log_context['subject_name'] = webconference.topic.subject.name
	log_context['subject_slug'] = webconference.topic.subject.slug
	log_context['topic_id'] = webconference.topic.id
	log_context['topic_name'] = webconference.topic.name
	log_context['topic_slug'] = webconference.topic.slug
	log_context['webconference_id'] = webconference.id
	log_context['webconference_name'] = webconference.name
	log_context['webconference_slug'] = webconference.slug
	log_context['webconference_online'] = str(int(time.time()))

	request.log_context = log_context

	return JsonResponse({'message':'ok'})

@log_decorator('resources', 'participate', 'webconference')
def finish(request):

	webconference = get_object_or_404(Webconference, slug = request.GET['roomName'])
	log_context = {}
	log_context['category_id'] = webconference.topic.subject.category.id
	log_context['category_name'] = webconference.topic.subject.category.name
	log_context['category_slug'] = webconference.topic.subject.category.slug
	log_context['subject_id'] = webconference.topic.subject.id
	log_context['subject_name'] = webconference.topic.subject.name
	log_context['subject_slug'] = webconference.topic.subject.slug
	log_context['topic_id'] = webconference.topic.id
	log_context['topic_name'] = webconference.topic.name
	log_context['topic_slug'] = webconference.topic.slug
	log_context['webconference_id'] = webconference.id
	log_context['webconference_name'] = webconference.name
	log_context['webconference_slug'] = webconference.slug
	log_context['webconference_finish'] = str(int(time.time()))

	request.log_context = log_context

	url = {'url': str(reverse_lazy('webconferences:view', kwargs = {'slug': request.GET['roomName']}))}
	return JsonResponse(url, safe=False)


class InsideView(LoginRequiredMixin, LogMixin, generic.DetailView):
	log_component = 'resources'
	log_action = 'view'
	log_resource = 'webconference'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webconference/view.html'
	model = Webconference
	context_object_name = 'webconference'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webconference = get_object_or_404(Webconference, slug = slug)

		if not has_resource_permissions(request.user, webconference):
			return redirect(reverse_lazy('subjects:home'))

		return super(InsideView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(InsideView, self).get_context_data(**kwargs)

		context['title'] = self.object.name

		context['topic'] = self.object.topic
		context['subject'] = self.object.topic.subject

		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['webconference_id'] = self.object.id
		self.log_context['webconference_name'] = self.object.name
		self.log_context['webconference_slug'] = self.object.slug
		self.log_context['webconference_view'] = str(int(time.time()))

		super(InsideView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['log_id'] = Log.objects.latest('id').id

		return context

class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = 'resources'
	log_action = 'create'
	log_resource = 'webconference'
	log_context = {}
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webconference/create.html'
	form_class = WebconferenceForm

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		if not has_subject_permissions(request.user, topic.subject):
			return redirect(reverse_lazy('subjects:home'))
		return super(CreateView, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		self.object = None

		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)
		pendencies_form = InlinePendenciesFormset(initial = [{'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize")), ("participate", _("Participate"))]}])

		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

	def post(self, request, *args, **kwargs):
		self.object = None

		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		pendencies_form = InlinePendenciesFormset(self.request.POST, initial = [{'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize")), ("participate", _("Participate"))]}])

		if (form.is_valid() and pendencies_form.is_valid()):
			return self.form_valid(form, pendencies_form)
		else:
			return self.form_invalid(form, pendencies_form)

	def get_initial(self):
		initial = super(CreateView, self).get_initial()

		slug = self.kwargs.get('slug', '')

		topic = get_object_or_404(Topic, slug = slug)
		initial['subject'] = topic.subject

		return initial

	def form_invalid(self, form, pendencies_form):
		# print (form,"       Form")
		# print (pendencies_form, "      Penden")
		for p_form in pendencies_form.forms:
			p_form.fields['action'].choices = [("", "-------"),("view", _("Visualize")), ("participate", _("Participate"))]
		print ("Invalid")
		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

	def form_valid(self, form, pendencies_form):

		self.object = form.save(commit = False)
		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		self.object.topic = topic
		self.object.order = topic.resource_topic.count() + 1

		if not self.object.topic.visible and not self.object.topic.repository:
			self.object.visible = False

		self.object.save()
		pendencies_form.instance = self.object
		pendencies_form.save(commit = False)

		for pform in pendencies_form.forms:
			pend_form = pform.save(commit = False)

			if not pend_form.action == "":
				pend_form.save()
		print ("Valid")
		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['webconference_id'] = self.object.id
		self.log_context['webconference_name'] = self.object.name
		self.log_context['webconference_slug'] = self.object.slug

		super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)

		context['title'] = _('Create Web Conference')

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('The Web conference "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

		success_url = reverse_lazy('webconferences:view', kwargs = {'slug': self.object.slug})

		if self.object.show_window:
			self.request.session['resources'] = {}
			self.request.session['resources']['new_page'] = True
			self.request.session['resources']['new_page_url'] = reverse('webconferences:window_view', kwargs = {'slug': self.object.slug})

			success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

		return success_url

class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
	log_component = 'resources'
	log_action = 'update'
	log_resource = 'webconference'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webconference/update.html'
	model = Webconference
	form_class = WebConferenceUpdateForm

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		if not has_subject_permissions(request.user, topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(UpdateView, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()

		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		pendencies_form = InlinePendenciesFormset(instance=self.object, initial = [{'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize")), ("participate", _("Participate"))]}])

		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()

		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		pendencies_form = InlinePendenciesFormset(self.request.POST, instance = self.object, initial = [{'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize")), ("participate", _("Participate"))]}])

		if (form.is_valid() and pendencies_form.is_valid()):
			return self.form_valid(form, pendencies_form)
		else:
			return self.form_invalid(form, pendencies_form)

	def form_invalid(self, form, pendencies_form):
		for p_form in pendencies_form.forms:
			p_form.fields['action'].choices = [("", "-------"),("view", _("Visualize")), ("participate", _("Participate"))]

		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

	def form_valid(self, form, pendencies_form):
		self.object = form.save(commit = False)

		if not self.object.topic.visible and not self.object.topic.repository:
			self.object.visible = False

		self.object.save()

		pendencies_form.instance = self.object
		pendencies_form.save(commit = False)

		for form in pendencies_form.forms:
			pend_form = form.save(commit = False)

			if not pend_form.action == "":
				pend_form.save()

		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['webconference_id'] = self.object.id
		self.log_context['webconference_name'] = self.object.name
		self.log_context['webconference_slug'] = self.object.slug

		super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)

		context['title'] = _('Update Web Conference')

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject
		context['resource'] = get_object_or_404(Webconference, slug = self.kwargs.get('slug', ''))

		return context

	def get_success_url(self):
		messages.success(self.request, _('The Web conference "%s" was updated successfully!')%(self.object.name))

		success_url = reverse_lazy('webconferences:view', kwargs = {'slug': self.object.slug})

		if self.object.show_window:
			self.request.session['resources'] = {}
			self.request.session['resources']['new_page'] = True
			self.request.session['resources']['new_page_url'] = reverse('webconferences:window_view', kwargs = {'slug': self.object.slug})

			success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

		return success_url

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = 'resources'
	log_action = 'delete'
	log_resource = 'webconference'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'resources/delete.html'
	model = Webconference
	context_object_name = 'resource'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webconference = get_object_or_404(Webconference, slug = slug)

		if not has_subject_permissions(request.user, webconference.topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(DeleteView, self).dispatch(request, *args, **kwargs)

	def get_success_url(self):
		messages.success(self.request, _('The web conference "%s" was removed successfully from virtual environment "%s"!')%(self.object.name, self.object.topic.subject.name))

		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['webconference_id'] = self.object.id
		self.log_context['webconference_name'] = self.object.name
		self.log_context['webconference_slug'] = self.object.slug

		super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

class ConferenceSettings(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webconference/config.html'
	model = Settings
	form_class = SettingsForm
	success_url = reverse_lazy("subjects:home")

	def get_object(self, queryset = None):
		return Settings.objects.last()

	def form_valid(self, form):
		form.save()

		messages.success(self.request, _("Conference settings updated successfully!"))

		return super(ConferenceSettings, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(ConferenceSettings, self).get_context_data(**kwargs)

		context['title'] = _('Web Conference Settings')

		return context

class StatisticsView(LoginRequiredMixin, LogMixin, generic.DetailView):
	log_component = 'resources'
	log_action = 'view_statistics'
	log_resource = 'webconference'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'
	model = Webconference
	template_name = 'webconference/relatorios.html'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webconference = get_object_or_404(Webconference, slug = slug)

		if not has_subject_permissions(request.user, webconference.topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(StatisticsView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(StatisticsView, self).get_context_data(**kwargs)

		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['webconference_id'] = self.object.id
		self.log_context['webconference_name'] = self.object.name
		self.log_context['webconference_slug'] = self.object.slug

		super(StatisticsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)


		context['title'] = _('Youtube Video Reports')

		slug = self.kwargs.get('slug')
		webconference = get_object_or_404(Webconference, slug = slug)

		date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language','') == 'pt-br' else "%m/%d/%Y %I:%M %p"
		if self.request.GET.get('language','') == "":
			start_date = datetime.datetime.now() - datetime.timedelta(30)
			end_date = datetime.datetime.now()
		else :
			start_date = datetime.datetime.strptime(self.request.GET.get('init_date',''),date_format)
			end_date = datetime.datetime.strptime(self.request.GET.get('end_date',''),date_format)
		context["init_date"] = start_date
		context["end_date"] = end_date
		alunos = webconference.students.all()
		if webconference.all_students :
			alunos = webconference.topic.subject.students.all()

		vis_ou = Log.objects.filter(context__contains={'webconference_id':webconference.id},resource="webconference",user_email__in=(aluno.email for aluno in alunos), datetime__range=(start_date,end_date + datetime.timedelta(minutes = 1))).filter(Q(action="view") | Q(action="initwebconference") | Q(action="participating"))
		did,n_did,history = str(_("Realized")),str(_("Unrealized")),str(_("Historic"))
		re = []
		data_n_did,data_history = [],[]
		json_n_did, json_history = {},{}

		for log_al in vis_ou.order_by("datetime"):
			data_history.append([str(alunos.get(email=log_al.user_email)),
			", ".join([str(x) for x in webconference.topic.subject.group_subject.filter(participants__email=log_al.user_email)]),
			log_al.action,log_al.datetime])

		json_history["data"] = data_history

		column_view,column_initwebconference,column_participate = str(_('View')),str(_('Enter')),str(_('Participate'))

		not_view = alunos.exclude(email__in=[log.user_email for log in vis_ou.filter(action="view").distinct("user_email")])
		index = 0
		for alun in not_view:
			data_n_did.append([index,str(alun),", ".join([str(x) for x in webconference.topic.subject.group_subject.filter(participants__email=alun.email)]),column_view, str(alun.email)])
			index += 1

		not_initwebconference = alunos.exclude(email__in=[log.user_email for log in vis_ou.filter(action="initwebconference").distinct("user_email")])
		for alun in not_initwebconference:
			data_n_did.append([index,str(alun),", ".join([str(x) for x in webconference.topic.subject.group_subject.filter(participants__email=alun.email)]),column_initwebconference, str(alun.email)])
			index += 1

		not_participate = alunos.exclude(email__in=[log.user_email for log in vis_ou.filter(action="participating").distinct("user_email")])
		for alun in not_participate:
			data_n_did.append([index,str(alun),", ".join([str(x) for x in webconference.topic.subject.group_subject.filter(participants__email=alun.email)]),column_participate, str(alun.email)])
			index += 1

		json_n_did["data"] = data_n_did


		context["json_n_did"] = json_n_did
		context["json_history"] = json_history
		c_visualizou = vis_ou.filter(action="view").distinct("user_email").count()
		c_initwebconference = vis_ou.filter(action="initwebconference").distinct("user_email").count()
		c_participate = vis_ou.filter(action="participating").distinct("user_email").count()
		re.append([str(_('Webconference')),did,n_did])

		re.append([column_view,c_visualizou, alunos.count() - c_visualizou])
		re.append([column_initwebconference,c_initwebconference, alunos.count() - c_initwebconference])
		re.append([column_participate,c_participate, alunos.count() - c_participate])

		context['view'] = column_view
		context['initwebconference'] = column_initwebconference
		context['participate'] = column_participate
		context['topic'] = webconference.topic
		context['subject'] = webconference.topic.subject
		context['webconference'] = webconference
		context['db_data'] = re
		context['title_chart'] = _('Actions about resource')
		context['title_vAxis'] = _('Quantity')

		context["n_did_table"] = n_did
		context["did_table"] = did
		context["history_table"] = history
		return context

from django.http import HttpResponse #used to send HTTP 404 error to ajax

class SendMessage(LoginRequiredMixin, LogMixin, generic.edit.FormView):
	log_component = 'resources'
	log_action = 'send'
	log_resource = 'webconference'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webconference/send_message.html'
	form_class = FormModalMessage

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webconference = get_object_or_404(Webconference, slug = slug)
		self.webconference = webconference

		if not has_subject_permissions(request.user, webconference.topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(SendMessage, self).dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		message = form.cleaned_data.get('comment')
		image = form.cleaned_data.get("image")
		users = (self.request.POST.get('users[]','')).split(",")
		user = self.request.user
		subject = self.webconference.topic.subject

		if (users[0] is not ''):
			for u in users:
				to_user = User.objects.get(email=u)
				talk, create = Conversation.objects.get_or_create(user_one=user,user_two=to_user)
				created = TalkMessages.objects.create(text=message,talk=talk,user=user,subject=subject,image=image)

				simple_notify = textwrap.shorten(strip_tags(message), width = 30, placeholder = "...")

				if image is not '':
					simple_notify += " ".join(_("[Photo]"))

				notification = {
					"type": "chat",
					"subtype": "subject",
					"space": subject.slug,
					"user_icon": created.user.image_url,
					"notify_title": str(created.user),
					"simple_notify": simple_notify,
					"view_url": reverse("chat:view_message", args = (created.id, ), kwargs = {}),
					"complete": render_to_string("chat/_message.html", {"talk_msg": created}, self.request),
					"container": "chat-" + str(created.user.id),
					"last_date": _("Last message in %s")%(formats.date_format(created.create_date, "SHORT_DATETIME_FORMAT"))
				}

				notification = json.dumps(notification)

				Group("user-%s" % to_user.id).send({'text': notification})

				ChatVisualizations.objects.create(viewed = False, message = created, user = to_user)

			success = str(_('The message was successfull sent!'))
			return JsonResponse({"message":success})
		erro = HttpResponse(str(_("No user selected!")))
		erro.status_code = 404
		return erro

	def get_context_data(self, **kwargs):
		context = super(SendMessage,self).get_context_data()
		context["webconference"] = get_object_or_404(Webconference, slug=self.kwargs.get('slug', ''))
		return context
