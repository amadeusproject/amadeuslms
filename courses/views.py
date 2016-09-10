from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin
from rolepermissions.mixins import HasRoleMixin
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from slugify import slugify
from rolepermissions.verifications import has_role
from django.db.models import Q

from .forms import CourseForm, CategoryForm, SubjectForm,TopicForm
from .models import Course, Subject, Category,Topic


class IndexView(LoginRequiredMixin, generic.ListView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	queryset = Course.objects.all()
	template_name = 'course/index.html'
	context_object_name = 'courses'
	paginate_by = 3

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)
		context['categories'] = Category.objects.all()

		return context

class CreateView(LoginRequiredMixin, HasRoleMixin, generic.edit.CreateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'course/create.html'
	form_class = CourseForm
	success_url = reverse_lazy('course:manage')
	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		print('Fooooiiii!!')
		self.object.save()

		return super(CreateView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Course created successfully!'))

		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class UpdateView(LoginRequiredMixin, HasRoleMixin, generic.UpdateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'course/update.html'
	model = Course
	form_class = CourseForm
	success_url = reverse_lazy('course:manage')

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		self.object.save()

		return super(UpdateView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Course edited successfully!'))

		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class View(LoginRequiredMixin, generic.DetailView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Course
	context_object_name = 'course'
	template_name = 'course/view.html'

	def get_context_data(self, **kwargs):
		context = super(View, self).get_context_data(**kwargs)
		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))
		subjects = Subject.objects.filter(Q(visible=True) | Q(professors__in=[self.request.user]) | Q(course = course))
		context['subjects'] = subjects

		return context

class DeleteView(LoginRequiredMixin, HasRoleMixin, generic.DeleteView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Course
	template_name = 'course/delete.html'
	success_url = reverse_lazy('course:manage')

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Course deleted successfully!'))

		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class FilteredView(LoginRequiredMixin, generic.ListView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'course/filtered.html'
	context_object_name = 'courses'
	paginate_by = 3

	def get_queryset(self):
		category = get_object_or_404(Category, slug = self.kwargs.get('slug'))
		return Course.objects.filter(category = category)

	def get_context_data(self, **kwargs):
		category = get_object_or_404(Category, slug = self.kwargs.get('slug'))
		context = super(FilteredView, self).get_context_data(**kwargs)
		context['categories'] = Category.objects.all()
		context['cat'] = category

		return context

class IndexCatView(LoginRequiredMixin, generic.ListView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	queryset = Category.objects.all()
	template_name = 'category/index.html'
	context_object_name = 'categories'
	paginate_by = 3

class CreateCatView(LoginRequiredMixin, HasRoleMixin, generic.edit.CreateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'category/create.html'
	form_class = CategoryForm
	success_url = reverse_lazy('course:manage_cat')

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		self.object.save()

		return super(CreateCatView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Category created successfully!'))

		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class UpdateCatView(LoginRequiredMixin, HasRoleMixin, generic.UpdateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'category/update.html'
	model = Category
	form_class = CategoryForm
	success_url = reverse_lazy('course:manage_cat')

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		self.object.save()

		return super(UpdateCatView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Category edited successfully!'))

		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class ViewCat(LoginRequiredMixin, generic.DetailView):
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Category
	template_name = 'category/view.html'
	context_object_name = 'category'

class DeleteCatView(LoginRequiredMixin, HasRoleMixin, generic.DeleteView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Category
	template_name = 'category/delete.html'
	success_url = reverse_lazy('course:manage_cat')

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Category deleted successfully!'))

		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class SubjectsView(LoginRequiredMixin, generic.ListView):

	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'subject/index.html'
	context_object_name = 'subjects'
	model = Subject

	def get_queryset(self):
		subject = get_object_or_404(Subject, slug = self.kwargs.get('slug'))
		course = subject.course
		context = course.subjects.filter(visible=True)
		if (self.request.user in subject.professors.all() or has_role(self.request.user,'system_admin')):
			context = course.subjects.all()
		return context

	def get_context_data(self, **kwargs):
		subject = get_object_or_404(Subject, slug = self.kwargs.get('slug'))
		context = super(SubjectsView, self).get_context_data(**kwargs)
		context['course'] = subject.course
		context['subject'] = subject
		context['topics'] = subject.topics.all()
		return context

class CreateTopicView(LoginRequiredMixin, HasRoleMixin, generic.edit.CreateView):

	allowed_roles = ['professor', 'system_admin','student']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'topic/create.html'
	form_class = TopicForm

	def get_success_url(self):
		return reverse_lazy('course:view_subject', kwargs={'slug' : self.object.subject.slug})

	def get_context_data(self, **kwargs):
		context = super(CreateTopicView, self).get_context_data(**kwargs)
		subject = get_object_or_404(Subject, slug = self.kwargs.get('slug'))
		context['course'] = subject.course
		context['subject'] = subject
		context['subjects'] = subject.course.subjects.filter(Q(visible=True) | Q(professors__in=[self.request.user]))
		if (has_role(self.request.user,'system_admin')):
			context['subjects'] = subject.course.subjects.all()
		return context

	def form_valid(self, form):
		subject = get_object_or_404(Subject, slug = self.kwargs.get('slug'))

		self.object = form.save(commit = False)
		self.object.subject = subject
		self.object.owner = self.request.user
		self.object.save()

		return super(CreateTopicView, self).form_valid(form)

class UpdateTopicView(LoginRequiredMixin, HasRoleMixin, generic.UpdateView):

	allowed_roles = ['professor', 'system_admin','student']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'topic/update.html'
	form_class = TopicForm

	def get_object(self, queryset=None):
	    return get_object_or_404(Topic, slug = self.kwargs.get('slug'))

	def get_success_url(self):
		return reverse_lazy('course:view_subject', kwargs={'slug' : self.object.subject.slug})

	def get_context_data(self, **kwargs):
		context = super(UpdateTopicView, self).get_context_data(**kwargs)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		context['course'] = topic.subject.course
		context['subject'] = topic.subject
		context['subjects'] = topic.subject.course.subjects.filter(Q(visible=True) | Q(professors__in=[self.request.user]))
		if (has_role(self.request.user,'system_admin')):
			context['subjects'] = topic.subject.course.subjects.all()
		return context

class CreateSubjectView(LoginRequiredMixin, HasRoleMixin, generic.edit.CreateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'subject/create.html'
	form_class = SubjectForm

	def get_success_url(self):
		return reverse_lazy('course:view_subject', kwargs={'slug' : self.object.slug})

	def get_context_data(self, **kwargs):
		context = super(CreateSubjectView, self).get_context_data(**kwargs)
		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))
		context['course'] = course
		context['subjects'] = course.subjects.filter(Q(visible=True) | Q(professors__in=[self.request.user]))
		if (has_role(self.request.user,'system_admin')):
			context['subjects'] = course.subjects.all()
		return context

	def form_valid(self, form):
		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))

		self.object = form.save(commit = False)
		self.object.course = course
		self.object.save()
		self.object.professors.add(self.request.user)

		return super(CreateSubjectView, self).form_valid(form)


class UpdateSubjectView(LoginRequiredMixin, HasRoleMixin, generic.UpdateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = 'subject/update.html'
	form_class = SubjectForm

	def get_object(self, queryset=None):
		context = get_object_or_404(Subject, slug = self.kwargs.get('slug'))
		return context

	def get_success_url(self):
		return reverse_lazy('course:view_subject', kwargs={'slug' : self.object.slug})

	def get_context_data(self, **kwargs):
		context = super(UpdateSubjectView, self).get_context_data(**kwargs)
		context['course'] = self.object.course
		context['subject'] = self.object
		context['subjects'] = self.object.course.subjects.filter(Q(visible=True) | Q(professors__in=[self.request.user]))
		if (has_role(self.request.user,'system_admin')):
			context['subjects'] = self.object.course.subjects.all()
		return context

class DeleteSubjectView(LoginRequiredMixin, HasRoleMixin, generic.DeleteView):

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = Subject
	template_name = 'subject/delete.html'

	def get_context_data(self, **kwargs):
		context = super(DeleteSubjectView, self).get_context_data(**kwargs)
		context['course'] = self.object.course
		context['subject'] = self.object
		context['subjects'] = self.object.course.subjects.filter(Q(visible=True) | Q(professors__in=[self.request.user]))
		if (has_role(self.request.user,'system_admin')):
			context['subjects'] = self.object.course.subjects.all()
		return context

	def get_success_url(self):
		return reverse_lazy('course:view_subject', kwargs={'slug' : self.object.course.subjects.all()[0].slug})
