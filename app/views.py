from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import decorator_from_middleware_with_args
from django.utils.decorators import decorator_from_middleware
from django.utils.decorators import method_decorator
from core.mixins import LogMixin

from courses.models import Course

class AppIndex(LoginRequiredMixin, LogMixin, TemplateView):
	log_action = "Acessou home"
	template_name = "home_professor.html"

	def render_to_response(self, context, **response_kwargs):
		context = {}

		if self.request.user.type_profile == 2:
			template = "home_student.html"
			context['courses'] = Course.objects.filter(user = self.request.user)
		else:
			template = self.get_template_names()
			context['courses'] = Course.objects.filter(user = self.request.user)

		context['title'] = 'Amadeus'

		return self.response_class(request = self.request, template = template, context = context, using = self.template_engine, **response_kwargs)