from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory, modelformset_factory

from log.models import Log
from log.mixins import LogMixin
from log.decorators import log_decorator, log_decorator_ajax
import time

from amadeus.permissions import has_subject_permissions, has_resource_permissions

from topics.models import Topic

from .forms import GoalsForm, MyGoalsForm, InlinePendenciesFormset, InlineGoalItemFormset
from .models import Goals, MyGoals

class AnsweredReport(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'
	
	template_name = 'goals/reports.html'	
	model = MyGoals
	context_object_name = 'answered'

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		goal = get_object_or_404(Goals, slug = slug)

		goals = MyGoals.objects.filter(item__goal = goal)

		return goals

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		if not has_resource_permissions(request.user, goals):
			return redirect(reverse_lazy('subjects:home'))

		return super(AnsweredReport, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(AnsweredReport, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', '')
		goals = get_object_or_404(Goals, slug = slug)

		context['title'] = _("Reports: Answered")
		
		context['goal'] = goals
		context['topic'] = goals.topic
		context['subject'] = goals.topic.subject

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

	def get_queryset(self):
		slug = self.kwargs.get('slug', '')
		goal = get_object_or_404(Goals, slug = slug)

		goals = MyGoals.objects.filter(user = self.request.user)

		return goals

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
		for p_form in pendencies_form.forms:
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
		messages.success(self.request, _('The Goals specification of the thopic %s was removed successfully!')%(self.object.topic.name))
		
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