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

class CreatePoll(generic.CreateView):

	# login_url = reverse_lazy("core:home")
	# redirect_field_name = 'next'
	model = Poll
	form_class = PollForm
	context_object_name = 'poll'
	template_name = 'poll/poll.html'
	# queryset = Course.objects.all()
	success_url = reverse_lazy('core:home')
	# def get_queryset(self):
	# 	return Course.objects.all()[0]

	def form_invalid(self, form,**kwargs):
		context = super(CreatePoll, self).form_invalid(form)
		answers = {}
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'limit_date'):
				answers[key] = self.request.POST[key]

		keys = sorted(answers)
		context.context_data['answers'] = answers
		context.context_data['keys'] = keys
		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)
		topic = Topic.objects.all()[0]
		self.object.student = self.request.user
		self.object.question = "question"
		self.object.topic = topic
		self.object.save()

		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'limit_date'):
				answer = Answer(answer=self.request.POST[key],order=key,poll=self.object)
				answer.save()

		return super(CreatePoll, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CreatePoll, self).get_context_data(**kwargs)
		course = Course.objects.all()[0]
		# print (self.object)
		context['course'] = course
		context['subject'] = course.subjects.all()[0]
		context['subjects'] = course.subjects.all()
		return context
