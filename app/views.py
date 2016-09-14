from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from core.mixins import LogMixin, NotificationMixin
from core.models import Notification, Action, Resource, Action_Resource
from users.models import User
from courses.models import Course

class AppIndex(LoginRequiredMixin, LogMixin, ListView, NotificationMixin):
	log_action = "Acessar"
	log_resource = "Home"
	
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "home.html"
	context_object_name = 'courses'
	paginate_by = 3

	not_action = "Acessar"
	not_resource = "home"

	def get_queryset(self):
		if self.request.user.is_staff:
			objects = Course.objects.all()
		else:
			objects = Notification.objects.filter(user = self.request.user)

		return objects

	def render_to_response(self, context, **response_kwargs):
		if self.request.user.is_staff:
			context['page_template'] = "home_admin_content.html"
		else:
			context['page_template'] = "home_teacher_student_content.html"
	
		context['title'] = 'Amadeus'

		if self.request.is_ajax():
			if self.request.user.is_staff:
				self.template_name = "home_admin_content.html"
			else:
				self.template_name = "home_teacher_student_content.html"
			

		super(AppIndex, self).createNotification("teste", not_resource="home", resource_link="/register")
		
		notifications = Notification.objects.filter(user= self.request.user, read=False)
		context['notifications'] = notifications
		
		return self.response_class(request = self.request, template = self.template_name, context = context, using = self.template_engine, **response_kwargs)


