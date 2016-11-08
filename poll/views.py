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
from django.db.models import Q
from django.urls import reverse

from .forms import PollForm
from .models import Poll, Answer, AnswersStudent
from core.mixins import LogMixin, NotificationMixin
from users.models import User
from core.models import Log
from courses.models import Course, Topic

import datetime

from django.http import JsonResponse

class ViewPoll(LoginRequiredMixin, LogMixin, generic.DetailView):
	log_component = "poll"
	log_resource = "poll"
	log_action = "viewed"
	log_context = {}

	model = Poll
	context_object_name = 'poll'
	template_name = 'poll/view.html'

	def get_object(self, queryset=None):
		poll = get_object_or_404(Poll, slug = self.kwargs.get('slug'))

		self.log_context['poll_id'] = poll.id
		self.log_context['poll_slug'] = poll.slug
		self.log_context['topic_id'] = poll.topic.id
		self.log_context['topic_name'] = poll.topic.name
		self.log_context['topic_slug'] = poll.topic.slug
		self.log_context['subject_id'] = poll.topic.subject.id
		self.log_context['subject_name'] = poll.topic.subject.name
		self.log_context['subject_slug'] = poll.topic.subject.slug
		self.log_context['course_id'] = poll.topic.subject.course.id
		self.log_context['course_name'] = poll.topic.subject.course.name
		self.log_context['course_slug'] = poll.topic.subject.course.slug
		self.log_context['course_category_id'] = poll.topic.subject.course.category.id
		self.log_context['course_category_name'] = poll.topic.subject.course.category.name

		super(ViewPoll, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['time_spent'] = str(datetime.datetime.now())
		self.request.session['log_id'] = Log.objects.latest('id').id

		return poll

	def get_context_data(self, **kwargs):
		context = super(ViewPoll, self).get_context_data(**kwargs)
		poll = self.object
		context["topic"] = poll.topic
		context['course'] = poll.topic.subject.course
		context['subject'] = poll.topic.subject
		context['subjects'] = poll.topic.subject.course.subjects.all()
		answered = AnswersStudent.objects.filter(poll = poll, student=self.request.user)
		if answered.count()<1:
			context['status'] = False
		else:
			context['status'] = answered[0].status

		return context


class CreatePoll(LoginRequiredMixin,HasRoleMixin, LogMixin, NotificationMixin,generic.CreateView):
	log_component = "poll"
	log_resource = "poll"
	log_action = "create"
	log_context = {}

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Poll
	form_class = PollForm
	context_object_name = 'poll'
	template_name = 'poll/create.html'

	def form_invalid(self, form,**kwargs):
		context = super(CreatePoll, self).form_invalid(form)
		answers = {}
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answers[key] = self.request.POST[key]

		keys = sorted(answers)
		context.context_data['answers'] = answers
		context.context_data['keys'] = keys
		context.context_data['form'] = form
		context.status_code = 400
		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		self.object.topic = topic
		self.object.name = str(self.object)
		self.object.save()

		super(CreatePoll, self).createNotification(message="created a Poll at "+ self.object.topic.name, actor=self.request.user,
			resource_name=self.object.name, resource_link= reverse('course:view_topic', args=[self.object.topic.slug]),
			users=self.object.topic.subject.students.all())
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answer = Answer(answer=self.request.POST[key],order=key,poll=self.object)
				answer.save()

		self.log_context['poll_id'] = self.object.id
		self.log_context['poll_slug'] = self.object.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['course_id'] = self.object.topic.subject.course.id
		self.log_context['course_name'] = self.object.topic.subject.course.name
		self.log_context['course_slug'] = self.object.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

		super(CreatePoll, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return JsonResponse({"view":reverse_lazy('course:poll:render_poll_view', kwargs={'slug' : self.object.slug}),
							"edit":reverse_lazy('course:poll:render_poll_edit', kwargs={'slug' : self.object.slug}),
							})


    # def get_success_url(self):
    #     self.success_url = redirect('course:poll:render_poll', slug = self.object.slug)
    #     return self.success_url

	def get_context_data(self, **kwargs):
		context = super(CreatePoll, self).get_context_data(**kwargs)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		context["topic"] = topic
		context['course'] = topic.subject.course
		context['subject'] = topic.subject
		context['subjects'] = topic.subject.course.subjects.all()
		return context

def render_poll_view(request, slug):
	template_name = 'poll/poll_view.html'
	context = {
		'poll': get_object_or_404(Poll, slug = slug)
	}
	return render(request, template_name, context)

def render_poll_edit(request, slug):
	template_name = 'poll/poll_edit.html'
	context = {
		'poll': get_object_or_404(Poll, slug = slug)
	}
	return render(request, template_name, context)

class UpdatePoll(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.UpdateView):
	log_component = "poll"
	log_resource = "poll"
	log_action = "update"
	log_context = {}

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Poll
	form_class = PollForm
	context_object_name = 'poll'
	template_name = 'poll/update.html'
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
		context.context_data['form'] = form
		context.status_code = 400
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

		self.log_context['poll_id'] = poll.id
		self.log_context['poll_slug'] = poll.slug
		self.log_context['topic_id'] = poll.topic.id
		self.log_context['topic_name'] = poll.topic.name
		self.log_context['topic_slug'] = poll.topic.slug
		self.log_context['subject_id'] = poll.topic.subject.id
		self.log_context['subject_name'] = poll.topic.subject.name
		self.log_context['subject_slug'] = poll.topic.subject.slug
		self.log_context['course_id'] = poll.topic.subject.course.id
		self.log_context['course_name'] = poll.topic.subject.course.name
		self.log_context['course_slug'] = poll.topic.subject.course.slug
		self.log_context['course_category_id'] = poll.topic.subject.course.category.id
		self.log_context['course_category_name'] = poll.topic.subject.course.category.name

		super(UpdatePoll, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return super(UpdatePoll, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(UpdatePoll, self).get_context_data(**kwargs)
		poll = self.object
		context['topic'] = poll.topic
		context['course'] = poll.topic.subject.course
		context['subject'] = poll.topic.subject
		context['subjects'] = poll.topic.subject.course.subjects.all()
		answers = {}
		for answer in poll.answers.all():
			answers[answer.order] = answer.answer

		keys = sorted(answers)
		context['answers'] = answers
		context['keys'] = keys

		return context

class DeletePoll(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.DeleteView):
	log_component = "poll"
	log_resource = "poll"
	log_action = "delete"
	log_context = {}

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Poll
	template_name = 'poll/remove.html'

	def dispatch(self, *args, **kwargs):
		poll = get_object_or_404(Poll, slug = self.kwargs.get('slug'))
		if(not has_object_permission('delete_poll', self.request.user, poll)):
			return self.handle_no_permission()
		return super(DeletePoll, self).dispatch(*args, **kwargs)


	def get_context_data(self, **kwargs):
		context = super(DeletePoll, self).get_context_data(**kwargs)
		context['course'] = self.object.topic.subject.course
		context['subject'] = self.object.topic.subject
		context['poll'] = self.object
		context["topic"] = self.object.topic
		context['subjects'] = self.object.topic.subject.course.subjects.filter(Q(visible=True) | Q(professors__in=[self.request.user]))
		if (has_role(self.request.user,'system_admin')):
			context['subjects'] = self.object.topic.subject.course.subjects.all()
		return context

	def get_success_url(self):
		self.log_context['poll_id'] = self.object.id
		self.log_context['poll_slug'] = self.object.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['course_id'] = self.object.topic.subject.course.id
		self.log_context['course_name'] = self.object.topic.subject.course.name
		self.log_context['course_slug'] = self.object.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

		super(DeletePoll, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('course:view_topic', kwargs={'slug' : self.object.topic.slug})


class AnswerPoll(generic.TemplateView):
	template_name = 'poll/answer.html'

class AnswerStudentPoll(LoginRequiredMixin, LogMixin, generic.CreateView):
	log_component = "poll"
	log_resource = "poll"
	log_action = "answer"
	log_context = {}

	model = AnswersStudent
	fields = ['status']
	context_object_name = 'answer'
	template_name = 'poll/answer_student.html'

	def dispatch(self, *args, **kwargs):
		if self.request.method == 'GET':
			self.request.session['time_spent'] = str(datetime.datetime.now())

		return super(AnswerStudentPoll, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		poll = get_object_or_404(Poll, slug = self.kwargs.get('slug'))
		answers = AnswersStudent(
            status = True,
            poll = poll,
            student = self.request.user,
        )
		answers.save()

		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken'):
				answers.answer.add(poll.answers.all().filter(order=key)[0])

		self.log_context['poll_id'] = poll.id
		self.log_context['poll_slug'] = poll.slug
		self.log_context['topic_id'] = poll.topic.id
		self.log_context['topic_name'] = poll.topic.name
		self.log_context['topic_slug'] = poll.topic.slug
		self.log_context['subject_id'] = poll.topic.subject.id
		self.log_context['subject_name'] = poll.topic.subject.name
		self.log_context['subject_slug'] = poll.topic.subject.slug
		self.log_context['course_id'] = poll.topic.subject.course.id
		self.log_context['course_name'] = poll.topic.subject.course.name
		self.log_context['course_slug'] = poll.topic.subject.course.slug
		self.log_context['course_category_id'] = poll.topic.subject.course.category.id
		self.log_context['course_category_name'] = poll.topic.subject.course.category.name

		date_time_click = datetime.datetime.strptime(self.request.session.get('time_spent'), "%Y-%m-%d %H:%M:%S.%f")
		_now = datetime.datetime.now()

		time_spent = _now - date_time_click

		secs = time_spent.total_seconds()
		hours = int(secs / 3600)
		minutes = int(secs / 60) % 60
		secs = secs % 60

		self.log_context['time_spent'] = {}
		self.log_context['time_spent']['hours'] = hours
		self.log_context['time_spent']['minutes'] = minutes
		self.log_context['time_spent']['seconds'] = secs

		super(AnswerStudentPoll, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return self.render_to_response(self.get_context_data(form = form), status = 200)

	def get_context_data(self, **kwargs):
		context = super(AnswerStudentPoll, self).get_context_data(**kwargs)
		poll = get_object_or_404(Poll, slug = self.kwargs.get('slug'))
		context['poll'] = poll
		context['topic'] = poll.topic
		context['course'] = poll.topic.subject.course
		context['subject'] = poll.topic.subject
		context['subjects'] = poll.topic.subject.course.subjects.all()

		answers = {}
		for answer in poll.answers.all():
			answers[answer.order] = answer.answer

		keys = sorted(answers)
		context['answers'] = answers
		context['keys'] = keys

		return context
