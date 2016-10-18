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
# from django.views.generic.edit import FormMixin

from .forms import ExamForm
from .models import Exam, Answer, AnswersStudent
from core.mixins import NotificationMixin
from users.models import User
from courses.models import Course, Topic

class ViewExam(LoginRequiredMixin,generic.DetailView):

	model = Exam
	context_object_name = 'exam'
	template_name = 'exam/view.html'

	def get_object(self, queryset=None):
	    return get_object_or_404(Exam, slug = self.kwargs.get('slug'))

	def get_context_data(self, **kwargs):
		context = super(ViewExam, self).get_context_data(**kwargs)
		exam = self.object
		context["topic"] = exam.topic
		context['course'] = exam.topic.subject.course
		context['subject'] = exam.topic.subject
		context['subjects'] = exam.topic.subject.course.subjects.all()

		answered = AnswersStudent.objects.filter(exam = exam, student=self.request.user)
		print (answered)
		if answered.count()<1:
			context['status'] = False
		else:
			context['status'] = answered[0].status
		return context



class CreateExam(LoginRequiredMixin,HasRoleMixin,generic.CreateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Exam
	form_class = ExamForm
	context_object_name = 'exam'
	template_name = 'exam/create.html'

	def form_invalid(self, form,**kwargs):
		context = super(CreateExam, self).form_invalid(form)
		answers = {}
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'begin_date' and key != 'limit_date' and key != 'all_students' and key != 'students'):
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
		self.object.save()

		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'begin_date' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answer = Answer(answer=self.request.POST[key],order=key,exam=self.object)
				answer.save()

		return self.render_to_response(self.get_context_data(form = form), status = 200)

	def get_context_data(self, **kwargs):
		context = super(CreateExam, self).get_context_data(**kwargs)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		context['course'] = topic.subject.course
		context['subject'] = topic.subject
		context['subjects'] = topic.subject.course.subjects.all()
		return context

class UpdateExam(LoginRequiredMixin,HasRoleMixin,generic.UpdateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Exam
	form_class = ExamForm
	context_object_name = 'exam'
	template_name = 'exam/update.html'
	success_url = reverse_lazy('core:home')

	def dispatch(self, *args, **kwargs):
		exam = get_object_or_404(Exam, slug = self.kwargs.get('slug'))
		if(not has_object_permission('edit_exam', self.request.user, exam)):
			return self.handle_no_permission()
		return super(UpdateExam, self).dispatch(*args, **kwargs)

	def get_object(self, queryset=None):
	    return get_object_or_404(Exam, slug = self.kwargs.get('slug'))

	def form_invalid(self, form,**kwargs):
		context = super(UpdateExam, self).form_invalid(form)
		answers = {}
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'begin_date' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answers[key] = self.request.POST[key]

		keys = sorted(answers)
		context.context_data['answers'] = answers
		context.context_data['keys'] = keys
		context.context_data['form'] = form
		context.status_code = 400
		return context

	def form_valid(self, form):
		exam = self.object
		exam = form.save(commit = False)
		exam.answers.all().delete()
		exam.save()


		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'begin_date' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answer = Answer(answer=self.request.POST[key],order=key,exam=exam)
				answer.save()

		return super(UpdateExam, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(UpdateExam, self).get_context_data(**kwargs)
		exam = self.object
		context['course'] = exam.topic.subject.course
		context['subject'] = exam.topic.subject
		context['subjects'] = exam.topic.subject.course.subjects.all()

		answers = {}
		for answer in exam.answers.all():
			answers[answer.order] = answer.answer

		keys = sorted(answers)
		context['answers'] = answers
		context['keys'] = keys

		return context

class DeleteExam(LoginRequiredMixin, HasRoleMixin, generic.DeleteView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Exam
	template_name = 'exam/remove.html'

	def dispatch(self, *args, **kwargs):
		exam = get_object_or_404(Exam, slug = self.kwargs.get('slug'))
		if(not has_object_permission('delete_exam', self.request.user, exam)):
			return self.handle_no_permission()
		return super(DeleteExam, self).dispatch(*args, **kwargs)


	def get_context_data(self, **kwargs):
		context = super(DeleteExam, self).get_context_data(**kwargs)
		context['course'] = self.object.topic.subject.course
		context['subject'] = self.object.topic.subject
		context['exam'] = self.object
		context['subjects'] = self.object.topic.subject.course.subjects.filter(Q(visible=True) | Q(professors__in=[self.request.user]))
		if (has_role(self.request.user,'system_admin')):
			context['subjects'] = self.object.topic.subject.course.subjects.all()
		return context

	def get_success_url(self):
		return reverse_lazy('course:view_topic', kwargs={'slug' : self.object.topic.slug})

class AnswerExam(generic.TemplateView):
	template_name = 'exam/answer.html'

class AnswerStudentExam(LoginRequiredMixin,generic.CreateView):

	model = AnswersStudent
	fields = ['status']
	context_object_name = 'answer'
	template_name = 'exam/answer_student.html'

	def form_valid(self, form):
		exam = get_object_or_404(Exam, slug = self.kwargs.get('slug'))
		answers = AnswersStudent(
            status = True,
            exam = exam,
            student = self.request.user,
        )
		answers.save()

		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken'):
				answers.answer.add(exam.answers.all().filter(order=key)[0])

		return self.render_to_response(self.get_context_data(form = form), status = 200)

	def get_context_data(self, **kwargs):
		context = super(AnswerStudentExam, self).get_context_data(**kwargs)
		print (self.kwargs.get('slug'))
		exam = get_object_or_404(Exam, slug = self.kwargs.get('slug'))
		context['exam'] = exam
		context['topic'] = exam.topic
		context['course'] = exam.topic.subject.course
		context['subject'] = exam.topic.subject
		context['subjects'] = exam.topic.subject.course.subjects.all()

		print (self.request.method)
		answers = {}
		for answer in exam.answers.all():
			answers[answer.order] = answer.answer

		keys = sorted(answers)
		context['answers'] = answers
		context['keys'] = keys

		return context
