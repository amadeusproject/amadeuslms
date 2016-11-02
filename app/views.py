from django.shortcuts import render
from django.views.generic import ListView
from django.views import View
from rolepermissions.mixins import HasRoleMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from core.mixins import NotificationMixin
from core.models import Notification, Action, Resource, Action_Resource
from users.models import User
from .models import EmailBackend
from .forms import EmailBackendForm
from courses.models import Course

class AppIndex(LoginRequiredMixin, ListView, NotificationMixin):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "home.html"
	context_object_name = 'objects'
	paginate_by = 10

	def get_queryset(self):
		if self.request.user.is_staff:
			objects = Course.objects.all()
		else:
			objects = Notification.objects.filter(user = self.request.user).order_by('-datetime')

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
			
		return self.response_class(request = self.request, template = self.template_name, context = context, using = self.template_engine, **response_kwargs)

class AmadeusSettings(LoginRequiredMixin, HasRoleMixin, View):
	allowed_roles = ['system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = EmailBackend
	template_name = 'admin_settings.html'
	form_class = EmailBackendForm
	success_url = reverse_lazy('app:settings')

	def get(self, request):
		return render(request, self.template_name, )



