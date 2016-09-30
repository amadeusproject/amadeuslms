from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin
from rolepermissions.mixins import HasRoleMixin
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from rolepermissions.verifications import has_role
from rolepermissions.verifications import has_object_permission
# from django.views.generic.edit import FormMixin

from .forms import PollForm
from .models import Poll, Answer
from core.mixins import NotificationMixin
from users.models import User
from courses.models import Course, Topic

class CreatePoll(LoginRequiredMixin,generic.CreateView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Poll
	form_class = PollForm
	context_object_name = 'poll'
	template_name = 'poll/create_update.html'
	success_url = reverse_lazy('core:home')

	def form_invalid(self, form,**kwargs):
		context = super(CreatePoll, self).form_invalid(form)
		answers = {}
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answers[key] = self.request.POST[key]

		keys = sorted(answers)
		context.context_data['answers'] = answers
		context.context_data['keys'] = keys
		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		self.object.topic = topic
		self.object.save()

		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answer = Answer(answer=self.request.POST[key],order=key,poll=self.object)
				answer.save()

		return super(CreatePoll, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CreatePoll, self).get_context_data(**kwargs)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		context['course'] = topic.subject.course
		context['subject'] = topic.subject
		context['subjects'] = topic.subject.course.subjects.all()
		return context

class UpdatePoll(LoginRequiredMixin,generic.UpdateView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Poll
	form_class = PollForm
	context_object_name = 'poll'
	template_name = 'poll/create_update.html'
	success_url = reverse_lazy('core:home')

	def dispatch(self, *args, **kwargs):
		poll = get_object_or_404(Poll, slug = self.kwargs.get('slug'))
		if(not has_object_permission('edit_poll', self.request.user, poll)):
			return self.handle_no_permission()
		return super(UpdatePoll, self).dispatch(*args, **kwargs)

	def get_object(self, queryset=None):
	    return get_object_or_404(Poll, slug = self.kwargs.get('slug'))

	def form_invalid(self, form,**kwargs):
		context = super(UpdatePoll, self).form_invalid(form)
		answers = {}
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answers[key] = self.request.POST[key]

		keys = sorted(answers)
		context.context_data['answers'] = answers
		context.context_data['keys'] = keys
		return context

	def form_valid(self, form):
		poll = self.object
		poll = form.save(commit = False)
		poll.answers.all().delete()
		poll.save()


		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answer = Answer(answer=self.request.POST[key],order=key,poll=poll)
				answer.save()

		return super(UpdatePoll, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(UpdatePoll, self).get_context_data(**kwargs)
		poll = self.object
		context['course'] = poll.topic.subject.course
		context['subject'] = poll.topic.subject
		context['subjects'] = poll.topic.subject.course.subjects.all()

		answers = {}
		for answer in poll.answers.all():
			# print (key.answer)
			answers[answer.order] = answer.answer

		keys = sorted(answers)
		context['answers'] = answers
		context['keys'] = keys

		return context
