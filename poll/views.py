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

# from .forms import CourseForm, UpdateCourseForm, CategoryForm, SubjectForm,TopicForm
# from .models import Course, Subject, Category,Topic, SubjectCategory
from core.mixins import NotificationMixin
from users.models import User
from courses.models import Course

class Poll(generic.TemplateView):

	# login_url = reverse_lazy("core:home")
	# redirect_field_name = 'next'
	# model = Course
	# context_object_name = 'course'
	template_name = 'poll/poll.html'
	# queryset = Course.objects.all()

	# def get_queryset(self):
	# 	return Course.objects.all()[0]

	def get_context_data(self, **kwargs):
		context = super(Poll, self).get_context_data(**kwargs)
		course = Course.objects.all()[0]
		context['course'] = course
		context['subject'] = course.subjects.all()[0]
		context['subjects'] = course.subjects.all()
		# if (has_role(self.request.user,'system_admin')):
		# 	context['subjects'] = self.object.course.subjects.all()
		return context
