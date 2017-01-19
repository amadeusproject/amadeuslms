from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from amadeus.permissions import has_subject_permissions

from topics.models import Topic

from .forms import WebpageForm, InlinePendenciesFormset
from .models import Webpage

class CreateView(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webpages/create.html'
	form_class = WebpageForm

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		if not has_subject_permissions(request.user, topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(CreateView, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		self.object = None
		
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		pendencies_form = InlinePendenciesFormset()

		return self.render_to_response(self.get_context_data(form = form,pendencies_form = pendencies_form))

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)

		context['title'] = _('Create Webpage')

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('Topic "%s" was created successfully!')%(self.object.name))

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})