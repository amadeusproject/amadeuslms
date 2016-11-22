from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.views.generic import ListView
from django.views import View, generic
from django.contrib import messages
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

class AmadeusSettings(LoginRequiredMixin, HasRoleMixin, generic.CreateView):
	allowed_roles = ['system_admin']
	login_url = reverse_lazy("core:home")
	model = EmailBackend
	template_name = 'admin_settings.html'
	form_class = EmailBackendForm
	#success_url = reverse_lazy('app:settings')

	def get_success_url(self):
		return reverse_lazy('app:settings', kwargs = {'page': self.kwargs['page']})

	def form_invalid(self, form):
		return self.render_to_response(self.get_context_data(form=form))

	def form_valid(self, form):
		try:
			self.object = EmailBackend.objects.latest('id')
			self.object.description = form.cleaned_data['description']
			self.object.host = form.cleaned_data['host']
			self.object.port = form.cleaned_data['port']
			self.object.username = form.cleaned_data['username']
			self.object.password = form.cleaned_data['password']
			self.object.safe_conection = form.cleaned_data['safe_conection']
			self.object.default_from_email = form.cleaned_data['default_from_email']
			self.object.save()
		except:
			self.object = form.save()
		messages.success(self.request, _('Changes saved.'))

		return super(AmadeusSettings, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(AmadeusSettings, self).get_context_data(**kwargs)
		context['page'] = self.kwargs.get('page')
		if not self.request.method == 'POST':
			try:
				setting = EmailBackend.objects.latest('id')
				context['form'] = EmailBackendForm(instance = setting)
			except:
				pass
		return context



