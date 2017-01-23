from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from amadeus.permissions import has_subject_permissions, has_resource_permissions

from topics.models import Topic

from .forms import WebpageForm, InlinePendenciesFormset
from .models import Webpage

class NewWindowView(LoginRequiredMixin, generic.DetailView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webpages/window_view.html'
	model = Webpage
	context_object_name = 'webpage'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webpage = get_object_or_404(Webpage, slug = slug)

		if not has_resource_permissions(request.user, webpage):
			return redirect(reverse_lazy('subjects:home'))

		return super(NewWindowView, self).dispatch(request, *args, **kwargs)

class InsideView(LoginRequiredMixin, generic.DetailView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webpages/view.html'
	model = Webpage
	context_object_name = 'webpage'	

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webpage = get_object_or_404(Webpage, slug = slug)

		if not has_resource_permissions(request.user, webpage):
			return redirect(reverse_lazy('subjects:home'))

		return super(InsideView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(InsideView, self).get_context_data(**kwargs)

		context['title'] = self.object.name
		
		context['topic'] = self.object.topic
		context['subject'] = self.object.topic.subject

		return context

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

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		pendencies_form = InlinePendenciesFormset(initial = [{'subject': topic.subject}])

		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

	def post(self, request, *args, **kwargs):
		self.object = None
		
		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		pendencies_form = InlinePendenciesFormset(self.request.POST, initial = [{'subject': topic.subject}])
		
		if (form.is_valid() and pendencies_form.is_valid()):
			return self.form_valid(form, pendencies_form)
		else:
			return self.form_invalid(form, pendencies_form)

	def get_initial(self):
		initial = super(CreateView, self).get_initial()

		slug = self.kwargs.get('slug', '')

		topic = get_object_or_404(Topic, slug = slug)
		initial['subject'] = topic.subject
		
		return initial

	def form_invalid(self, form, pendencies_form):
		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

	def form_valid(self, form, pendencies_form):
		self.object = form.save(commit = False)

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		self.object.topic = topic
		self.object.order = topic.resource_topic.count() + 1

		self.object.save()

		pendencies_form.instance = self.object
		pendencies_form.save()
        
		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)

		context['title'] = _('Create Webpage')

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('The Webpage "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

		success_url = reverse_lazy('webpages:view', kwargs = {'slug': self.object.slug})

		if self.object.show_window:
			self.request.session['resources'] = {}
			self.request.session['resources']['new_page'] = True
			self.request.session['resources']['new_page_url'] = reverse('webpages:window_view', kwargs = {'slug': self.object.slug})

			success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

		return success_url

class UpdateView(LoginRequiredMixin, generic.UpdateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webpages/update.html'
	model = Webpage
	form_class = WebpageForm

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		if not has_subject_permissions(request.user, topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(UpdateView, self).dispatch(request, *args, **kwargs)

	# def get(self, request, *args, **kwargs):
	# 	self.object = self.get_queryset()

	# 	form_class = self.get_form_class()
	# 	form = self.get_form(form_class)

	# 	slug = self.kwargs.get('topic_slug', '')
	# 	topic = get_object_or_404(Topic, slug = slug)

	# 	pendencies_form = InlinePendenciesFormset(instance = self.object)

	# 	return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

	def post(self, request, *args, **kwargs):
		self.object = None
		
		form_class = self.get_form_class()
		form = self.get_form(form_class)

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		pendencies_form = InlinePendenciesFormset(self.request.POST, initial = [{'subject': topic.subject}])
		
		if (form.is_valid() and pendencies_form.is_valid()):
			return self.form_valid(form, pendencies_form)
		else:
			return self.form_invalid(form, pendencies_form)
	
	def form_invalid(self, form, pendencies_form):
		return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

	def form_valid(self, form, pendencies_form):
		self.object = form.save(commit = False)

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		self.object.topic = topic
		self.object.order = topic.resource_topic.count() + 1

		self.object.save()

		pendencies_form.instance = self.object
		pendencies_form.save()
        
		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)

		context['title'] = _('Update Webpage')

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject

		if self.request.POST:
			context['form'] = WebpageForm(self.request.POST, instance=self.object, initial = {'subject': topic.subject})
			context['pendencies_form'] = InlinePendenciesFormset(self.request.POST, instance=self.object)
		else:
			context['form'] = WebpageForm(instance=self.object, initial = {'subject': topic.subject})
			context['pendencies_form'] = InlinePendenciesFormset(instance=self.object)

		return context

	def get_success_url(self):
		messages.success(self.request, _('The Webpage "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

		success_url = reverse_lazy('webpages:view', kwargs = {'slug': self.object.slug})

		if self.object.show_window:
			self.request.session['resources'] = {}
			self.request.session['resources']['new_page'] = True
			self.request.session['resources']['new_page_url'] = reverse('webpages:window_view', kwargs = {'slug': self.object.slug})

			success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

		return success_url