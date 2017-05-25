from django.views import generic
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from braces import views as braces_mixins

from .models import MailSender
from .forms import MailSenderForm

class MailSenderSettings(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'mailsender/update.html'
	model = MailSender
	form_class = MailSenderForm
	success_url = reverse_lazy("subjects:home")

	def get_object(self, queryset = None):
		return MailSender.objects.get(id = 1)

	def form_valid(self, form):
		form.save()

		messages.success(self.request, _("Mail Sender configuration updated successfully!"))

		return super(MailSenderSettings, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(MailSenderSettings, self).get_context_data(**kwargs)

		context['title'] = _('Mail Sender')
		context['settings_menu_active'] = "settings_menu_active"

		return context