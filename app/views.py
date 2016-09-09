from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from core.mixins import LogMixin, NotificationMixin
from core.models import Notification, Action, Resource, Action_Resource
from users.models import User
from courses.models import Course

class AppIndex(LoginRequiredMixin, LogMixin, TemplateView, NotificationMixin):
	log_action = "Acessar"
	log_resource = "Home"
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = "home_professor.html"

	not_action = "Acessar"
	not_resource = "home"

	def render_to_response(self, context, **response_kwargs):
		context = {}

		if self.request.user.type_profile == 2:
			template = "home_student.html"
			context['courses'] = Course.objects.filter(user = self.request.user)
		else:
			template = self.get_template_names()
			context['courses'] = Course.objects.filter(user = self.request.user)

		context['title'] = 'Amadeus'
		self.createNotification("teste")
		notifications = Notification.objects.filter(user= self.request.user, read=False)
		
		context['notifications'] = notifications
		print(notifications)

		return self.response_class(request = self.request, template = template, context = context, using = self.template_engine, **response_kwargs)

	def createNotification(self, mensagem='', actor=None, users = User.objects.all(), not_action = '', not_resource=''): #the default will be a broadcast
		action = Action.objects.filter(name = not_action)
		resource = Resource.objects.filter(name = self.not_resource)
		print(action)
		if not action:
			action = Action(name = self.not_action)
			action.save()
		else:
			action = action[0]

		if not resource:
			resource = Resource(name = self.not_resource)
			resource.save()
		else:
			resource = resource[0]

		action_resource = Action_Resource.objects.filter(action = action, resource = resource)

		if not action_resource:
			action_resource = Action_Resource(action = action, resource = resource)
			action_resource.save()
		else:
			action_resource = action_resource[0]

		for user in users:
			print(user)
			notification = Notification(user=user, actor= actor, message=mensagem, action_resource= action_resource)
			notification.save()

