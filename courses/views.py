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

from .forms import CourseForm, CategoryForm, SubjectForm
from .models import Course, Subject, Category


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
	# paginate_by = 5

	def get_queryset(self):
		subject = get_object_or_404(Subject, slug = self.kwargs.get('slug'))
		course = subject.course
		return course.subjects.filter(visible=True)

	def get_context_data(self, **kwargs):
		# print ("Deu Certo")
		subject = get_object_or_404(Subject, slug = self.kwargs.get('slug'))
		# print (course)
		# print (course.slug)
		# print (course.subjects.filter(visible=True))
		context = super(SubjectsView, self).get_context_data(**kwargs)
		context['course'] = subject.course
		context['subject'] = subject
		context['topics'] = subject.topics.all()
		# print (context)
		return context

# class CreateSubjectView(LoginRequiredMixin, HasRoleMixin, generic.edit.CreateView):
#
# 	allowed_roles = ['professor', 'system_admin']
# 	login_url = reverse_lazy("core:home")
# 	redirect_field_name = 'next'
# 	template_name = 'module/create.html'
# 	form_class = SubjectForm
#
# 	def get_success_url(self):
# 		return reverse_lazy('course:manage_mods', kwargs={'slug' : self.object.course.slug})
#
# 	def get_context_data(self, **kwargs):
# 		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))
# 		context = super(CreateModView, self).get_context_data(**kwargs)
# 		context['course'] = course
#
# 		return context
#
# 	def form_valid(self, form):
# 		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))
#
# 		self.object = form.save(commit = False)
# 		self.object.slug = slugify(self.object.name)
# 		self.object.course = course
# 		self.object.save()
#
# 		return super(CreateModView, self).form_valid(form)
#
# 	def render_to_response(self, context, **response_kwargs):
# 		messages.success(self.request, _('Module created successfully!'))
#
# 		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)
#
# class UpdateModView(LoginRequiredMixin, HasRoleMixin, generic.UpdateView):
#
# 	allowed_roles = ['professor', 'system_admin']
# 	login_url = reverse_lazy("core:home")
# 	redirect_field_name = 'next'
# 	template_name = 'module/update.html'
# 	model = Module
# 	form_class = ModuleForm
#
# 	def get_success_url(self):
# 		return reverse_lazy('course:manage_mods', kwargs={'slug' : self.object.course.slug})
#
# 	def get_context_data(self, **kwargs):
# 		course = get_object_or_404(Course, slug = self.kwargs.get('slug_course'))
# 		context = super(UpdateModView, self).get_context_data(**kwargs)
# 		context['course'] = course
#
# 		return context
#
# 	def form_valid(self, form):
# 		self.object = form.save(commit = False)
# 		self.object.slug = slugify(self.object.name)
# 		self.object.save()
#
# 		return super(UpdateModView, self).form_valid(form)
#
# 	def render_to_response(self, context, **response_kwargs):
# 		messages.success(self.request, _('Module edited successfully!'))
#
# 		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)
#
# class DeleteModView(LoginRequiredMixin, HasRoleMixin, generic.DeleteView):
#
# 	allowed_roles = ['professor', 'system_admin']
# 	login_url = reverse_lazy("core:home")
# 	redirect_field_name = 'next'
# 	model = Module
# 	template_name = 'module/delete.html'
#
# 	def get_success_url(self):
# 		return reverse_lazy('course:manage_mods', kwargs={'slug' : self.object.course.slug})
#
# 	def get_context_data(self, **kwargs):
# 		course = get_object_or_404(Course, slug = self.kwargs.get('slug_course'))
# 		context = super(DeleteModView, self).get_context_data(**kwargs)
# 		context['course'] = course
#
# 		return context
#
# 	def render_to_response(self, context, **response_kwargs):
# 		messages.success(self.request, _('Module deleted successfully!'))
#
# 		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

# class ViewSubject(LoginRequiredMixin, generic.DetailView):
# 	login_url = reverse_lazy("core:home")
# 	redirect_field_name = 'next'
# 	model = Course
# 	template_name = 'subject/index.html'
# 	context_object_name = 'course'
