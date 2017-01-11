from django.views import generic
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from braces import views as braces_mixins

from .models import Security
from .forms import SecurityForm

class SecuritySettings(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'security/update.html'
	model = Security
	form_class = SecurityForm
	success_url = reverse_lazy("subjects:home")

	def get_object(self, queryset = None):
		return Security.objects.get(id = 1)

	def form_valid(self, form):
		form.save()

		messages.success(self.request, _("Security settings updated successfully!"))

		return super(SecuritySettings, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(SecuritySettings, self).get_context_data(**kwargs)

		context['title'] = _('Security')
		context['settings_menu_active'] = "settings_menu_active"

		return context
