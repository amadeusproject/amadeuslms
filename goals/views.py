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
from django.forms import formset_factory, modelformset_factory
from django.http import JsonResponse

from log.models import Log
from log.mixins import LogMixin
from log.decorators import log_decorator, log_decorator_ajax
import time

from amadeus.permissions import has_subject_permissions, has_resource_permissions

from topics.models import Topic
from users.models import User

from .utils import brodcast_dificulties
from .forms import GoalsForm, MyGoalsForm, InlinePendenciesFormset, InlineGoalItemFormset
from .models import Goals, MyGoals

import datetime
from log.models import Log
from chat.models import Conversation, TalkMessages, ChatVisualizations
from users.models import User
from subjects.models import Subject

from webpage.forms import FormModalMessage

from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import formats, timezone
import textwrap
from django.utils.html import strip_tags
import json
from channels import Group

class Reports(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'
	
	template_name = 'goals/reports.html'	
	model = Goals
	totals = {}

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_subject_permissions(request.user, goals):
			return redirect(reverse_lazy('subjects:home'))

		return super(Reports, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		goal = get_object_or_404(Goals, slug = slug)

		users = goal.topic.subject.students.values_list('id')

		submited = Log.objects.filter(user_id__in = users, action = 'submit', resource = 'goals', context__contains = {"goals_id": goal.id}).values_list('user_id')

		submited_users = User.objects.filter(id__in = submited)

		self.totals['answered'] = submited_users.count()
		self.totals['unanswered'] = users.count() - self.totals['answered']
		
		return goal

	def get_context_data(self, **kwargs):
		context = super(Reports, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		context['title'] = _("Reports")
		
		context['goal'] = goals
		context['topic'] = goals.topic
		context['subject'] = goals.topic.subject
		context['totals'] = self.totals

		return context

class AnsweredReport(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'
	
	template_name = 'goals/_answered.html'	
	context_object_name = 'students'

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		goal = get_object_or_404(Goals, slug = slug)

		users = goal.topic.subject.students.values_list('id')

		submited = Log.objects.filter(user_id__in = users, action = 'submit', resource = 'goals', context__contains = {"goals_id": goal.id}).values_list('user_id')

		submited_users = User.objects.filter(id__in = submited)

		return submited_users

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_subject_permissions(request.user, goals):
			return redirect(reverse_lazy('subjects:home'))

		return super(AnsweredReport, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(AnsweredReport, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)
		
		context['goal'] = goals

		return context

class UnansweredReport(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'
	
	template_name = 'goals/_unanswered.html'	
	context_object_name = 'students'

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		goal = get_object_or_404(Goals, slug = slug)

		users = goal.topic.subject.students.values_list('id', flat = True)

		submited = Log.objects.filter(user_id__in = users, action = 'submit', resource = 'goals', context__contains = {"goals_id": goal.id}).values_list('user_id', flat = True)

		users = [i for i in users if i not in submited]
		
		submited_users = User.objects.filter(id__in = users)

		return submited_users

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_subject_permissions(request.user, goals):
			return redirect(reverse_lazy('subjects:home'))

		return super(UnansweredReport, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(UnansweredReport, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)
		
		context['goal'] = goals

		return context

class HistoryReport(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'
	
	template_name = 'goals/_history.html'	
	context_object_name = 'records'

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		goal = get_object_or_404(Goals, slug = slug)

		rows = Log.objects.filter(context__contains = {"goals_id": goal.id}).exclude(action = 'view_reports')
		
		return rows

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_subject_permissions(request.user, goals):
			return redirect(reverse_lazy('subjects:home'))

		return super(HistoryReport, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(HistoryReport, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)
		
		context['goal'] = goals

		return context

class InsideView(LoginRequiredMixin, LogMixin, generic.ListView):
	log_component = "resources"
	log_action = "view"
	log_resource = "my_goals"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'goals/view.html'
	model = Goals
	context_object_name = 'itens'

	students = None

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		goal = get_object_or_404(Goals, slug = slug)

		if has_subject_permissions(self.request.user, goal.topic.subject):
			self.students = User.objects.filter(subject_student = goal.topic.subject).order_by('social_name', 'username')

			goals = MyGoals.objects.filter(user = self.students.first(), item__goal = goal)
		else:
			goals = MyGoals.objects.filter(user = self.request.user, item__goal = goal)

		return goals

	def post(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goal = get_object_or_404(Goals, slug = slug)

		user = request.POST.get('selected_student', None)

		if has_subject_permissions(request.user, goal.topic.subject):
			self.students = User.objects.filter(subject_student = goal.topic.subject).order_by('social_name', 'username')

			if not user is None:
				self.object_list = MyGoals.objects.filter(user__email = user, item__goal = goal)
			else:
				self.object_list = MyGoals.objects.filter(user = self.request.user, item__goal = goal)	
		else:
			self.object_list = MyGoals.objects.filter(user = self.request.user, item__goal = goal)

		return self.render_to_response(self.get_context_data())

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_resource_permissions(request.user, goals):
			return redirect(reverse_lazy('subjects:home'))

		return super(InsideView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(InsideView, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		context['title'] = _("My Goals")
		
		context['goal'] = goals
		context['topic'] = goals.topic
		context['subject'] = goals.topic.subject

		if not self.students is None:
			context['sub_students'] = self.students
			context['student'] = self.request.POST.get('selected_student', self.students.first().email)

		self.log_context['category_id'] = goals.topic.subject.category.id
		self.log_context['category_name'] = goals.topic.subject.category.name
		self.log_context['category_slug'] = goals.topic.subject.category.slug
		self.log_context['subject_id'] = goals.topic.subject.id
		self.log_context['subject_name'] = goals.topic.subject.name
		self.log_context['subject_slug'] = goals.topic.subject.slug
		self.log_context['topic_id'] = goals.topic.id
		self.log_context['topic_name'] = goals.topic.name
		self.log_context['topic_slug'] = goals.topic.slug
		self.log_context['goals_id'] = goals.id
		self.log_context['goals_name'] = goals.name
		self.log_context['goals_slug'] = goals.slug
		self.log_context['timestamp_start'] = str(int(time.time()))

		super(InsideView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 

		self.request.session['log_id'] = Log.objects.latest('id').id

		return context

class NewWindowSubmit(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = "resources"
	log_action = "submit"
	log_resource = "goals"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'goals/window_submit.html'
	form_class = MyGoalsForm

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_resource_permissions(request.user, goals):
			return redirect(reverse_lazy('subjects:home'))

		if has_subject_permissions(request.user, goals.topic.subject):
			return redirect(reverse_lazy('goals:view', kwargs = {'slug': goals.slug}))

		if MyGoals.objects.filter(item__goal = goals, user = request.user).exists():
			return redirect(reverse_lazy('goals:view', args = (), kwargs = {'slug': slug}))

		return super(NewWindowSubmit, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		self.object = None
		
		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		MyGoalsFormset = formset_factory(MyGoalsForm, extra = 0)
		my_goals_formset = MyGoalsFormset(initial = [{'item': x.id, 'value': x.ref_value} for x in goals.item_goal.all()])

		self.log_action = "view"

		self.log_context['category_id'] = goals.topic.subject.category.id
		self.log_context['category_name'] = goals.topic.subject.category.name
		self.log_context['category_slug'] = goals.topic.subject.category.slug
		self.log_context['subject_id'] = goals.topic.subject.id
		self.log_context['subject_name'] = goals.topic.subject.name
		self.log_context['subject_slug'] = goals.topic.subject.slug
		self.log_context['topic_id'] = goals.topic.id
		self.log_context['topic_name'] = goals.topic.name
		self.log_context['topic_slug'] = goals.topic.slug
		self.log_context['goals_id'] = goals.id
		self.log_context['goals_name'] = goals.name
		self.log_context['goals_slug'] = goals.slug
		self.log_context['timestamp_start'] = str(int(time.time()))

		super(NewWindowSubmit, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 

		self.request.session['log_id'] = Log.objects.latest('id').id

		self.log_context = {}
		
		return self.render_to_response(self.get_context_data(my_goals_formset = my_goals_formset))

	def post(self, request, *args, **kwargs):
		self.object = None
		
		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		MyGoalsFormset = formset_factory(MyGoalsForm, extra = 0)
		my_goals_formset = MyGoalsFormset(self.request.POST, initial = [{'item': x.id, 'value': x.ref_value} for x in goals.item_goal.all()])
		
		if (my_goals_formset.is_valid()):
			return self.form_valid(my_goals_formset)
		else:
			return self.form_invalid(my_goals_formset)

	def form_invalid(self, my_goals_formset):
		return self.render_to_response(self.get_context_data(my_goals_formset = my_goals_formset))

	def form_valid(self, my_goals_formset):
		for forms in my_goals_formset.forms:
			form = forms.save(commit = False)
			form.user = self.request.user

			form.save()

		dificulties = self.request.POST.get('dificulties', None)

		if not dificulties is None:
			slug = self.kwargs.get('slug', '')
			goals = get_object_or_404(Goals, slug = slug)

			message = _("#Dificulty(ies) found in %s")%(str(goals)) + ":<p>" + dificulties + "</p>"

			brodcast_dificulties(self.request, message, goals.topic.subject)

		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(NewWindowSubmit, self).get_context_data(**kwargs)
		
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		context['title'] = goals.name

		context['goals'] = goals

		return context

	def get_success_url(self):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		messages.success(self.request, _('Your goals for %s was save successfully!')%(goals.topic.name))

		success_url = reverse_lazy('goals:view', kwargs = {'slug': slug})

		self.log_context['category_id'] = goals.topic.subject.category.id
		self.log_context['category_name'] = goals.topic.subject.category.name
		self.log_context['category_slug'] = goals.topic.subject.category.slug
		self.log_context['subject_id'] = goals.topic.subject.id
		self.log_context['subject_name'] = goals.topic.subject.name
		self.log_context['subject_slug'] = goals.topic.subject.slug
		self.log_context['topic_id'] = goals.topic.id
		self.log_context['topic_name'] = goals.topic.name
		self.log_context['topic_slug'] = goals.topic.slug
		self.log_context['goals_id'] = goals.id
		self.log_context['goals_name'] = goals.name
		self.log_context['goals_slug'] = goals.slug

		super(NewWindowSubmit, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 

		return success_url

class SubmitView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = "resources"
	log_action = "submit"
	log_resource = "goals"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'goals/submit.html'
	form_class = MyGoalsForm

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_resource_permissions(request.user, goals):
			return redirect(reverse_lazy('subjects:home'))

		if has_subject_permissions(request.user, goals.topic.subject):
			return redirect(reverse_lazy('goals:view', kwargs = {'slug': goals.slug}))

		if MyGoals.objects.filter(item__goal = goals, user = request.user).exists():
			return redirect(reverse_lazy('goals:view', args = (), kwargs = {'slug': slug}))

		return super(SubmitView, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		self.object = None
		
		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		MyGoalsFormset = formset_factory(MyGoalsForm, extra = 0)
		my_goals_formset = MyGoalsFormset(initial = [{'item': x.id, 'value': x.ref_value} for x in goals.item_goal.all()])

		self.log_action = "view"

		self.log_context['category_id'] = goals.topic.subject.category.id
		self.log_context['category_name'] = goals.topic.subject.category.name
		self.log_context['category_slug'] = goals.topic.subject.category.slug
		self.log_context['subject_id'] = goals.topic.subject.id
		self.log_context['subject_name'] = goals.topic.subject.name
		self.log_context['subject_slug'] = goals.topic.subject.slug
		self.log_context['topic_id'] = goals.topic.id
		self.log_context['topic_name'] = goals.topic.name
		self.log_context['topic_slug'] = goals.topic.slug
		self.log_context['goals_id'] = goals.id
		self.log_context['goals_name'] = goals.name
		self.log_context['goals_slug'] = goals.slug
		self.log_context['timestamp_start'] = str(int(time.time()))

		super(SubmitView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 

		self.request.session['log_id'] = Log.objects.latest('id').id

		self.log_context = {}
		
		return self.render_to_response(self.get_context_data(my_goals_formset = my_goals_formset))

	def post(self, request, *args, **kwargs):
		self.object = None

		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		MyGoalsFormset = formset_factory(MyGoalsForm, extra = 0)
		my_goals_formset = MyGoalsFormset(self.request.POST, initial = [{'item': x.id, 'value': x.ref_value} for x in goals.item_goal.all()])
		
		if (my_goals_formset.is_valid()):
			return self.form_valid(my_goals_formset)
		else:
			return self.form_invalid(my_goals_formset)

	def form_invalid(self, my_goals_formset):
		return self.render_to_response(self.get_context_data(my_goals_formset = my_goals_formset))

	def form_valid(self, my_goals_formset):
		for forms in my_goals_formset.forms:
			form = forms.save(commit = False)
			form.user = self.request.user

			form.save()

		dificulties = self.request.POST.get('dificulties', None)

		if not dificulties is None:
			slug = self.kwargs.get('slug', '')
			goals = get_object_or_404(Goals, slug = slug)

			message = _("#Dificulty(ies) found in %s")%(str(goals)) + ":<p>" + dificulties + "</p>"

			brodcast_dificulties(self.request, message, goals.topic.subject)

		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(SubmitView, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		context['title'] = goals.name
		
		context['goals'] = goals
		context['topic'] = goals.topic
		context['subject'] = goals.topic.subject

		return context

	def get_success_url(self):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		messages.success(self.request, _('Your goals for %s was save successfully!')%(goals.topic.name))

		success_url = reverse_lazy('goals:view', kwargs = {'slug': slug})

		self.log_context['category_id'] = goals.topic.subject.category.id
		self.log_context['category_name'] = goals.topic.subject.category.name
		self.log_context['category_slug'] = goals.topic.subject.category.slug
		self.log_context['subject_id'] = goals.topic.subject.id
		self.log_context['subject_name'] = goals.topic.subject.name
		self.log_context['subject_slug'] = goals.topic.subject.slug
		self.log_context['topic_id'] = goals.topic.id
		self.log_context['topic_name'] = goals.topic.name
		self.log_context['topic_slug'] = goals.topic.slug
		self.log_context['goals_id'] = goals.id
		self.log_context['goals_name'] = goals.name
		self.log_context['goals_slug'] = goals.slug

		super(SubmitView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 

		return success_url

class UpdateSubmit(LoginRequiredMixin, LogMixin, generic.UpdateView):
	log_component = "resources"
	log_action = "update"
	log_resource = "my_goals"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'goals/submit.html'
	form_class = MyGoalsForm

	def get_object(self, queryset = None):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		return MyGoals.objects.filter(item__goal = goals, user = self.request.user)[0]

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_resource_permissions(request.user, goals):
			return redirect(reverse_lazy('subjects:home'))

		if goals.limit_submission_date < timezone.now():
			messages.error(self.request, _('The date limit to submit your Goals specification for the topic %s has passed, so you can\'t edit your values!')%(goals.topic.name))
			return redirect(reverse_lazy('goals:view', kwargs = {'slug': slug}))

		return super(UpdateSubmit, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()

		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		MyGoalsFormset = modelformset_factory(MyGoals, form = MyGoalsForm, extra = 0)
		my_goals_formset = MyGoalsFormset(queryset = MyGoals.objects.filter(user = request.user, item__goal = goals))
		
		return self.render_to_response(self.get_context_data(my_goals_formset = my_goals_formset))

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()

		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		MyGoalsFormset = modelformset_factory(MyGoals, form = MyGoalsForm, extra = 0)
		my_goals_formset = MyGoalsFormset(self.request.POST, queryset = MyGoals.objects.filter(user = request.user, item__goal = goals))
		
		if (my_goals_formset.is_valid()):
			return self.form_valid(my_goals_formset)
		else:
			return self.form_invalid(my_goals_formset)

	def form_invalid(self, my_goals_formset):
		return self.render_to_response(self.get_context_data(my_goals_formset = my_goals_formset))

	def form_valid(self, my_goals_formset):
		for forms in my_goals_formset.forms:
			form = forms.save(commit = False)

			form.save()

		dificulties = self.request.POST.get('dificulties', None)

		if not dificulties is None:
			slug = self.kwargs.get('slug', '')
			goals = get_object_or_404(Goals, slug = slug)

			message = _("#Dificulty(ies) found in %s")%(str(goals)) + ":<p>" + dificulties + "</p>"

			brodcast_dificulties(self.request, message, goals.topic.subject)

		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(UpdateSubmit, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		context['title'] = goals.name
		
		context['goals'] = goals
		context['topic'] = goals.topic
		context['subject'] = goals.topic.subject

		return context

	def get_success_url(self):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		messages.success(self.request, _('Your goals for %s was update successfully!')%(goals.topic.name))

		success_url = reverse_lazy('goals:view', kwargs = {'slug': slug})

		self.log_context['category_id'] = goals.topic.subject.category.id
		self.log_context['category_name'] = goals.topic.subject.category.name
		self.log_context['category_slug'] = goals.topic.subject.category.slug
		self.log_context['subject_id'] = goals.topic.subject.id
		self.log_context['subject_name'] = goals.topic.subject.name
		self.log_context['subject_slug'] = goals.topic.subject.slug
		self.log_context['topic_id'] = goals.topic.id
		self.log_context['topic_name'] = goals.topic.name
		self.log_context['topic_slug'] = goals.topic.slug
		self.log_context['goals_id'] = goals.id
		self.log_context['goals_name'] = goals.name
		self.log_context['goals_slug'] = goals.slug

		super(UpdateSubmit, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 

		return success_url

class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = "resources"
	log_action = "create"
	log_resource = "goals"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'goals/create.html'
	form_class = GoalsForm

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

		pendencies_form = InlinePendenciesFormset(initial = [{'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize")), ("submit", _("Submit"))]}])
		goalitems_form = InlineGoalItemFormset()

		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form, goalitems_form = goalitems_form))

	def post(self, request, *args, **kwargs):
		self.object = None
		
		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		pendencies_form = InlinePendenciesFormset(self.request.POST, initial = [{'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize")), ("submit", _("Submit"))]}])
		goalitems_form = InlineGoalItemFormset(self.request.POST)

		if (form.is_valid() and pendencies_form.is_valid() and goalitems_form.is_valid()):
			return self.form_valid(form, pendencies_form, goalitems_form)
		else:
			return self.form_invalid(form, pendencies_form, goalitems_form)

	def get_initial(self):
		initial = super(CreateView, self).get_initial()

		slug = self.kwargs.get('slug', '')

		topic = get_object_or_404(Topic, slug = slug)
		initial['subject'] = topic.subject
		initial['topic'] = topic
		
		return initial

	def form_invalid(self, form, pendencies_form, goalitems_form):
		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		for p_form in pendencies_form.forms:
			print(p_form.initial['subject'])
			p_form.fields['action'].choices = [("", "-------"),("view", _("Visualize")), ("submit", _("Submit"))]

		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form, goalitems_form = goalitems_form))

	def form_valid(self, form, pendencies_form, goalitems_form):
		self.object = form.save(commit = False)

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		self.object.topic = topic
		self.object.order = topic.resource_topic.count() + 1

		self.object.all_students = True

		if not self.object.topic.visible and not self.object.topic.repository:
			self.object.visible = False

		self.object.save()

		pendencies_form.instance = self.object
		pendencies_form.save(commit = False)
		
		for pform in pendencies_form.forms:
			pend_form = pform.save(commit = False)

			if not pend_form.action == "":
				pend_form.save()

		goalitems_form.instance = self.object
		goalitems_form.save(commit = False)

		g_order = 1

		for gform in goalitems_form.forms:
			goal_form = gform.save(commit = False)

			if not goal_form.description == "":
				goal_form.order = g_order
				goal_form.save()

				g_order += 1
		
		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['goals_id'] = self.object.id
		self.log_context['goals_name'] = self.object.name
		self.log_context['goals_slug'] = self.object.slug

		super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 
		
		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)

		context['title'] = _('Create Topic Goals')

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('The Goals specification for the topic %s was realized successfully!')%(self.object.topic.name))

		if has_subject_permissions(self.request.user, self.object.topic.subject):
			success_url = reverse_lazy('goals:view', kwargs = {'slug': self.object.slug})
		else:
			success_url = reverse_lazy('goals:submit', kwargs = {'slug': self.object.slug})

			if self.object.show_window:
				self.request.session['resources'] = {}
				self.request.session['resources']['new_page'] = True
				self.request.session['resources']['new_page_url'] = reverse('goals:window_submit', kwargs = {'slug': self.object.slug})

				success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

		return success_url

class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
	log_component = "resources"
	log_action = "update"
	log_resource = "goals"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'goals/update.html'
	model = Goals
	form_class = GoalsForm
	context_object_name = 'goal'

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

		pendencies_form = InlinePendenciesFormset(instance = self.object, initial = [{'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize")), ("submit", _("Submit"))]}])
		goalitems_form = InlineGoalItemFormset(instance = self.object)

		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form, goalitems_form = goalitems_form))

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		
		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		pendencies_form = InlinePendenciesFormset(self.request.POST, instance = self.object, initial = [{'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize")), ("submit", _("Submit"))]}])
		goalitems_form = InlineGoalItemFormset(self.request.POST, instance = self.object)

		if (form.is_valid() and pendencies_form.is_valid() and goalitems_form.is_valid()):
			return self.form_valid(form, pendencies_form, goalitems_form)
		else:
			return self.form_invalid(form, pendencies_form, goalitems_form)
	
	def form_invalid(self, form, pendencies_form, goalitems_form):
		for p_form in pendencies_form.forms:
			p_form.fields['action'].choices = [("", "-------"),("view", _("Visualize")), ("submit", _("Submit"))]

		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form, goalitems_form = goalitems_form))

	def form_valid(self, form, pendencies_form, goalitems_form):
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

		goalitems_form.instance = self.object
		goalitems_form.save(commit = False)

		g_order = 1

		for gform in goalitems_form.forms:
			goal_form = gform.save(commit = False)

			if not goal_form.description == "":
				goal_form.order = g_order
				goal_form.save()

				g_order += 1
		
		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['goals_id'] = self.object.id
		self.log_context['goals_name'] = self.object.name
		self.log_context['goals_slug'] = self.object.slug

		super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 
		
		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)

		context['title'] = _('Update Topic Goals')

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('The Goals specification for the topic %s was updated successfully!')%(self.object.topic.name))

		if has_subject_permissions(self.request.user, self.object.topic.subject):
			success_url = reverse_lazy('goals:view', kwargs = {'slug': self.object.slug})
		else:
			success_url = reverse_lazy('goals:submit', kwargs = {'slug': self.object.slug})

			if self.object.show_window:
				self.request.session['resources'] = {}
				self.request.session['resources']['new_page'] = True
				self.request.session['resources']['new_page_url'] = reverse('goals:window_submit', kwargs = {'slug': self.object.slug})

				success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

		return success_url

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = "resources"
	log_action = "delete"
	log_resource = "goals"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'resources/delete.html'
	model = Goals
	context_object_name = 'resource'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_subject_permissions(request.user, goals.topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(DeleteView, self).dispatch(request, *args, **kwargs)

	def get_success_url(self):
		messages.success(self.request, _('The Goals specification of the topic %s was removed successfully!')%(self.object.topic.name))
		
		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['goals_id'] = self.object.id
		self.log_context['goals_name'] = self.object.name
		self.log_context['goals_slug'] = self.object.slug

		super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

@log_decorator_ajax('resources', 'view_reports', 'goals')
def reports_log(request, goal, report):
	action = request.GET.get('action')

	if action == 'open':
		goals = get_object_or_404(Goals, slug = goal)

		log_context = {}
		log_context['category_id'] = goals.topic.subject.category.id
		log_context['category_name'] = goals.topic.subject.category.name
		log_context['category_slug'] = goals.topic.subject.category.slug
		log_context['subject_id'] = goals.topic.subject.id
		log_context['subject_name'] = goals.topic.subject.name
		log_context['subject_slug'] = goals.topic.subject.slug
		log_context['topic_id'] = goals.topic.id
		log_context['topic_name'] = goals.topic.name
		log_context['topic_slug'] = goals.topic.slug
		log_context['goals_id'] = goals.id
		log_context['goals_name'] = goals.name
		log_context['goals_slug'] = goals.slug
		log_context['goals_report'] = report
		log_context['timestamp_start'] = str(int(time.time()))
		log_context['timestamp_end'] = '-1'

		request.log_context = log_context

		log_id = Log.objects.latest('id').id

		return JsonResponse({'message': 'ok', 'log_id': log_id})

	return JsonResponse({'message': 'ok'})

class StatisticsView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view_statistics'
    log_resource = 'goals'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Goals
    template_name = 'goals/relatorios.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        goal = get_object_or_404(Goals, slug = slug)

        if not has_subject_permissions(request.user, goal.topic.subject):
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
        self.log_context['goals_id'] = self.object.id
        self.log_context['goals_name'] = self.object.name
        self.log_context['goals_slug'] = self.object.slug

        super(StatisticsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)


        context['title'] = _('Goals Reports')

        slug = self.kwargs.get('slug')
        goal = get_object_or_404(Goals, slug = slug)

        date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language','') == 'pt-br' else "%m/%d/%Y %I:%M %p"
        if self.request.GET.get('language','') == "":
            start_date = datetime.datetime.now() - datetime.timedelta(30)
            end_date = datetime.datetime.now()
        else :
            start_date = datetime.datetime.strptime(self.request.GET.get('init_date',''),date_format)
            end_date = datetime.datetime.strptime(self.request.GET.get('end_date',''),date_format)
        context["init_date"] = start_date
        context["end_date"] = end_date
        alunos = goal.students.all()
        if goal.all_students :
        	alunos = goal.topic.subject.students.all()

        vis_ou = Log.objects.filter(context__contains={'goals_id':goal.id},resource="goals",user_email__in=(aluno.email for aluno in alunos), datetime__range=(start_date,end_date + datetime.timedelta(minutes = 1))).filter(Q(action="view") | Q(action="submit"))
        did,n_did,history = str(_("Realized")),str(_("Unrealized")),str(_("Historic"))
        re = []
        data_n_did,data_history = [],[]
        json_n_did, json_history = {},{}

        for log_al in vis_ou.order_by("datetime"):
            data_history.append([str(alunos.get(email=log_al.user_email)),
            ", ".join([str(x) for x in goal.topic.subject.group_subject.filter(participants__email=log_al.user_email)]),
            log_al.action,log_al.datetime])
        
        json_history["data"] = data_history

        column_view,column_submit = str(_('View')),str(_('Submitted'))

        not_view = alunos.exclude(email__in=[log.user_email for log in vis_ou.filter(action="view").distinct("user_email")])
        index = 0
        for alun in not_view:
            data_n_did.append([index,str(alun),", ".join([str(x) for x in goal.topic.subject.group_subject.filter(participants__email=alun.email)]),column_view, str(alun.email)])
            index += 1
        
        not_watch = alunos.exclude(email__in=[log.user_email for log in vis_ou.filter(action="submit").distinct("user_email")])
        for alun in not_watch:
            data_n_did.append([index,str(alun),", ".join([str(x) for x in goal.topic.subject.group_subject.filter(participants__email=alun.email)]),column_submit, str(alun.email)])
            index += 1

        json_n_did["data"] = data_n_did


        context["json_n_did"] = json_n_did
        context["json_history"] = json_history
        c_visualizou = vis_ou.filter(action="view").distinct("user_email").count()
        c_submit = vis_ou.filter(action="submit").distinct("user_email").count()
        re.append([str(_('Goals')),did,n_did])
        
        re.append([column_view,c_visualizou, alunos.count() - c_visualizou])
        re.append([column_submit,c_submit, alunos.count() - c_submit])

        context['view'] = column_view
        context['submit'] = column_submit
        context['topic'] = goal.topic
        context['subject'] = goal.topic.subject
        context['goal'] = goal
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
    log_resource = 'goals'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'goals/send_message.html'
    form_class = FormModalMessage

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        goal = get_object_or_404(Goals, slug = slug)
        self.goal = goal
        
        if not has_subject_permissions(request.user, goal.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SendMessage, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        message = form.cleaned_data.get('comment')
        image = form.cleaned_data.get("image",'')
        users = (self.request.POST.get('users[]','')).split(",")
        user = self.request.user
        subject = self.goal.topic.subject

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
        context["goal"] = get_object_or_404(Goals, slug=self.kwargs.get('slug', ''))
        return context
    
