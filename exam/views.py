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

from .forms import ExamForm
from .models import Exam, Answer
from core.mixins import NotificationMixin
from users.models import User
from courses.models import Course, Topic

class CreatePoll(LoginRequiredMixin,generic.CreateView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Exam
	form_class = PollForm
	context_object_name = 'exam'
	template_name = 'exam/form_exam.html'
	success_url = reverse_lazy('core:home')

	def form_valid(self, form):
		self.object = form.save(commit = False)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		self.object.topic = topic
		self.object.save()

		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'beginDate' and key != 'endDate'):
				answer = Answer(answer=self.request.POST[key],order=key,poll=self.object)
				answer.save()

		return super(CreateExam, self).form_valid(form)

    def form_invalid(self, form,**kwargs):
		context = super(CreateExam, self).form_invalid(form)
		answers = {}
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'beginDate' and key != 'endDate'):
				answers[key] = self.request.POST[key]

		keys = sorted(answers)
		context.context_data['answers'] = answers
		context.context_data['keys'] = keys
		return context

class UpdateExam(LoginRequiredMixin,generic.UpdateView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Exam
	form_class = ExamForm
	context_object_name = 'exam'
	template_name = 'poll/form_exam.html'
	success_url = reverse_lazy('core:home')

    def dispatch(self, *args, **kwargs):
		poll = get_object_or_404(Poll, slug = self.kwargs.get('slug'))
		if(not has_object_permission('edit_exam', self.request.user, exam)):
			return self.handle_no_permission()
		return super(UpdateExam, self).dispatch(*args, **kwargs)

	def get_object(self, queryset=None):
	    return get_object_or_404(Poll, slug = self.kwargs.get('slug'))

	def form_valid(self, form):
		poll = self.object
		poll = form.save(commit = False)
		poll.answers.all().delete()
		poll.save()

		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'beginDate' and key != 'endDate'):
				answer = Answer(answer=self.request.POST[key],order=key,exam=exam)
				answer.save()

		return super(UpdateExam, self).form_valid(form)

	def form_invalid(self, form,**kwargs):
		context = super(UpdateExam, self).form_invalid(form)
		answers = {}
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'beginDate' and key != 'endDate'):
				answers[key] = self.request.POST[key]

		keys = sorted(answers)
		context.context_data['answers'] = answers
		context.context_data['keys'] = keys
		return context
