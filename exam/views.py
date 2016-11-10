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
from datetime import datetime
import time
# from django.views.generic.edit import FormMixin

from .forms import ExamForm
from .models import Exam, Answer, AnswersStudent
from core.mixins import LogMixin, NotificationMixin
from core.models import Log
from users.models import User
from courses.models import Course, Topic

class ViewExam(LoginRequiredMixin, LogMixin, generic.DetailView):
	log_component = 'exam'
	log_resource = 'exam'
	log_action = 'viewed'
	log_context = {}

	model = Exam
	context_object_name = 'exam'
	template_name = 'exam/view.html'

	def get_object(self, queryset=None):
	    return get_object_or_404(Topic, slug = self.kwargs.get('slug'))

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

		self.log_context['exam_id'] = exam.id
		self.log_context['topic_id'] = exam.topic.id
		self.log_context['topic_name'] = exam.topic.name
		self.log_context['topic_slug'] = exam.topic.slug
		self.log_context['subject_id'] = exam.topic.subject.id
		self.log_context['subject_name'] = exam.topic.subject.name
		self.log_context['subject_slug'] = exam.topic.subject.slug
		self.log_context['course_id'] = exam.topic.subject.course.id
		self.log_context['course_name'] = exam.topic.subject.course.name
		self.log_context['course_slug'] = exam.topic.subject.course.slug
		self.log_context['course_category_id'] = exam.topic.subject.course.category.id
		self.log_context['course_category_name'] = exam.topic.subject.course.category.name
		self.request.session['time_spent'] = str(int(time.time()))

		super(ViewExam, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['log_id'] = Log.objects.latest('id').id

		return context



class CreateExam(LoginRequiredMixin,HasRoleMixin, LogMixin, NotificationMixin, generic.CreateView):
	log_component = 'exam'
	log_resource = 'exam'
	log_action = 'create'
	log_context = {}

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
		self.object.name = str(self.object)
		self.object.save()

		super(CreateExam, self).createNotification(message="created an Exam "+ self.object.name, actor=self.request.user,
			resource_name=self.object.name, resource_link= reverse('course:exam:view_exam', args=[self.object.slug]), 
			users=self.object.topic.subject.students.all())
		for key in self.request.POST:
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'begin_date' and key != 'limit_date' and key != 'all_students' and key != 'students'):
				answer = Answer(answer=self.request.POST[key],order=key,exam=self.object)
				answer.save()

		self.log_context['exam_id'] = self.object.id
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

		super(CreateExam, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return self.render_to_response(self.get_context_data(form = form), status = 200)

	def get_context_data(self, **kwargs):
		context = super(CreateExam, self).get_context_data(**kwargs)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		context['course'] = topic.subject.course
		context['subject'] = topic.subject
		context['subjects'] = topic.subject.course.subjects.all()
		return context

class UpdateExam(LoginRequiredMixin,HasRoleMixin, LogMixin, generic.UpdateView):
	log_component = 'exam'
	log_resource = 'exam'
	log_action = 'update'
	log_context = {}

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
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'begin_date' and key != 'limit_date' and key!= 'exibe'  and key != 'all_students' and key != 'students'):
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
			if(key != 'csrfmiddlewaretoken' and key != 'name' and key != 'begin_date' and key != 'limit_date' and key!= 'exibe'  and key != 'all_students' and key != 'students'):
				answer = Answer(answer=self.request.POST[key],order=key,exam=exam)
				answer.save()

		self.log_context['exam_id'] = self.object.id
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

		super(UpdateExam, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

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

class DeleteExam(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.DeleteView):
	log_component = 'exam'
	log_resource = 'exam'
	log_action = 'delete'
	log_context = {}

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
		self.log_context['exam_id'] = self.object.id
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

		super(DeleteExam, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('course:view_topic', kwargs={'slug' : self.object.topic.slug})

class AnswerExam(generic.TemplateView):
	template_name = 'exam/answer.html'

class AnswerStudentExam(LoginRequiredMixin, LogMixin, generic.CreateView):
	log_component = 'exam'
	log_resource = 'exam'
	log_action = 'answer'
	log_context = {}

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

		self.log_context['exam_id'] = exam.id
		self.log_context['topic_id'] = exam.topic.id
		self.log_context['topic_name'] = exam.topic.name
		self.log_context['topic_slug'] = exam.topic.slug
		self.log_context['subject_id'] = exam.topic.subject.id
		self.log_context['subject_name'] = exam.topic.subject.name
		self.log_context['subject_slug'] = exam.topic.subject.slug
		self.log_context['course_id'] = exam.topic.subject.course.id
		self.log_context['course_name'] = exam.topic.subject.course.name
		self.log_context['course_slug'] = exam.topic.subject.course.slug
		self.log_context['course_category_id'] = exam.topic.subject.course.category.id
		self.log_context['course_category_name'] = exam.topic.subject.course.category.name

		date_time_click = datetime.strptime(self.request.session.get('time_spent'), "%Y-%m-%d %H:%M:%S.%f")
		_now = datetime.now()

		time_spent = _now - date_time_click

		secs = time_spent.total_seconds()
		hours = int(secs / 3600)
		minutes = int(secs / 60) % 60
		secs = secs % 60

		self.log_context['timestamp_end'] = str(int(time.time()))
		self.log_context['time_spent'] = {}
		self.log_context['time_spent']['hours'] = hours
		self.log_context['time_spent']['minutes'] = minutes
		self.log_context['time_spent']['seconds'] = secs

		super(AnswerStudentExam, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

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

		self.log_context['timestamp_start'] = str(int(time.time()))
		self.request.session['time_spent'] = str(datetime.now())

		return context

class MultipleChoiceQuestion(generic.TemplateView):
	template_name = 'exam/multiple_choice_question.html'


class MultipleChoiceAnswer(generic.TemplateView):
	template_name = 'exam/multiple_choice_answer.html'


class DiscursiveQuestion(generic.TemplateView):
	template_name = 'exam/discursive_question.html'


class TrueOrFalseQuestion(generic.TemplateView):
	template_name = 'exam/true_or_false_question.html'


class TrueOrFalseAnswer(generic.TemplateView):
	template_name = 'exam/true_or_false_answer.html'


class GapFillingQuestion(generic.TemplateView):
	template_name = 'exam/gap_filling_question.html'

class GapFillingAnswer(generic.TemplateView):
	template_name = 'exam/gap_filling_answer.html'
