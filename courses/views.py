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
from rest_framework import generics, permissions

from .serializers import CourseSerializer
from .forms import CourseForm, CategoryForm, ModuleForm
from .models import Course, Module, Category


class IndexView(LoginRequiredMixin, generic.ListView):

	login_url = '/'
	redirect_field_name = 'next'
	queryset = Course.objects.all()
	template_name = 'course/index.html'
	context_object_name = 'courses'
	paginate_by = 3

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)
		context['categories'] = Category.objects.all()

		return context

class CreateView(HasRoleMixin, LoginRequiredMixin, generic.edit.CreateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	template_name = 'course/create.html'
	form_class = CourseForm
	success_url = reverse_lazy('app:course:manage')

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		self.object.save()

		return super(CreateView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Course created successfully!'))
    
		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class UpdateView(HasRoleMixin, LoginRequiredMixin, generic.UpdateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	template_name = 'course/update.html'
	model = Course
	form_class = CourseForm
	success_url = reverse_lazy('app:course:manage')

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		self.object.save()

		return super(UpdateView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Course edited successfully!'))
    
		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class View(LoginRequiredMixin, generic.DetailView):

	login_url = '/'
	redirect_field_name = 'next'
	model = Course
	context_object_name = 'course'
	template_name = 'course/view.html'

class DeleteView(HasRoleMixin, LoginRequiredMixin, generic.DeleteView):

	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	model = Course
	template_name = 'course/delete.html'
	success_url = reverse_lazy('app:course:manage')

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Course deleted successfully!'))
    
		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class FilteredView(LoginRequiredMixin, generic.ListView):

	login_url = '/'
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

	login_url = '/'
	redirect_field_name = 'next'
	queryset = Category.objects.all()
	template_name = 'category/index.html'
	context_object_name = 'categories'
	paginate_by = 3

class CreateCatView(HasRoleMixin, LoginRequiredMixin, generic.edit.CreateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	template_name = 'category/create.html'
	form_class = CategoryForm
	success_url = reverse_lazy('app:course:manage_cat')

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		self.object.save()

		return super(CreateCatView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Category created successfully!'))
    
		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class UpdateCatView(HasRoleMixin, LoginRequiredMixin, generic.UpdateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	template_name = 'category/update.html'
	model = Category
	form_class = CategoryForm
	success_url = reverse_lazy('app:course:manage_cat')

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		self.object.save()

		return super(UpdateCatView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Category edited successfully!'))
    
		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class ViewCat(LoginRequiredMixin, generic.DetailView):
	login_url = '/'
	redirect_field_name = 'next'
	model = Category
	template_name = 'category/view.html'
	context_object_name = 'category'

class DeleteCatView(HasRoleMixin, LoginRequiredMixin, generic.DeleteView):
	
	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	model = Category
	template_name = 'category/delete.html'
	success_url = reverse_lazy('app:course:manage_cat')

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Category deleted successfully!'))
    
		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class ModulesView(LoginRequiredMixin, generic.ListView):

	login_url = '/'
	redirect_field_name = 'next'
	template_name = 'module/index.html'
	context_object_name = 'modules'
	paginate_by = 1

	def get_queryset(self):
		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))
		return Module.objects.filter(course = course)

	def get_context_data(self, **kwargs):
		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))
		context = super(ModulesView, self).get_context_data(**kwargs)
		context['course'] = course

		return context

class CreateModView(HasRoleMixin, LoginRequiredMixin, generic.edit.CreateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	template_name = 'module/create.html'
	form_class = ModuleForm

	def get_success_url(self):
		return reverse_lazy('app:course:manage_mods', kwargs={'slug' : self.object.course.slug})

	def get_context_data(self, **kwargs):
		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))
		context = super(CreateModView, self).get_context_data(**kwargs)
		context['course'] = course

		return context

	def form_valid(self, form):
		course = get_object_or_404(Course, slug = self.kwargs.get('slug'))

		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		self.object.course = course
		self.object.save()

		return super(CreateModView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Module created successfully!'))
    
		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class UpdateModView(HasRoleMixin, LoginRequiredMixin, generic.UpdateView):

	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	template_name = 'module/update.html'
	model = Module
	form_class = ModuleForm

	def get_success_url(self):
		return reverse_lazy('app:course:manage_mods', kwargs={'slug' : self.object.course.slug})

	def get_context_data(self, **kwargs):
		course = get_object_or_404(Course, slug = self.kwargs.get('slug_course'))
		context = super(UpdateModView, self).get_context_data(**kwargs)
		context['course'] = course

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.object.slug = slugify(self.object.name)
		self.object.save()

		return super(UpdateModView, self).form_valid(form)

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Module edited successfully!'))
    
		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

class DeleteModView(HasRoleMixin, LoginRequiredMixin, generic.DeleteView):

	allowed_roles = ['professor', 'system_admin']
	login_url = '/'
	redirect_field_name = 'next'
	model = Module
	template_name = 'module/delete.html'

	def get_success_url(self):
		return reverse_lazy('app:course:manage_mods', kwargs={'slug' : self.object.course.slug})

	def get_context_data(self, **kwargs):
		course = get_object_or_404(Course, slug = self.kwargs.get('slug_course'))
		context = super(DeleteModView, self).get_context_data(**kwargs)
		context['course'] = course

		return context

	def render_to_response(self, context, **response_kwargs):
		messages.success(self.request, _('Module deleted successfully!'))
    
		return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine)

# API Views
class CourseListApiView(generics.ListCreateAPIView):

	serializer_class = CourseSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get_queryset(self):
		return Course.objects.all()