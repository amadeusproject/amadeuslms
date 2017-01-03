from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from .models import Category
from django.core.urlresolvers import reverse_lazy
from rolepermissions.verifications import has_role

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.mixins import LoginRequiredMixin

from rolepermissions.mixins import HasRoleMixin
from .forms import CategoryForm

from braces import views
from subjects.models import Subject

from log.mixins import LogMixin
from log.decorators import log_decorator_ajax
from log.models import Log

import time

from users.models import User

class IndexView(views.SuperuserRequiredMixin, LoginRequiredMixin, ListView):

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    queryset = Category.objects.all()
    template_name = 'categories/list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        result = super(IndexView, self).get_queryset()

       	
        return result

    def render_to_response(self, context, **response_kwargs):
        if self.request.user.is_staff:
            context['page_template'] = "categories/home_admin_content.html"
        else:
            context['page_template'] = "categories/home_teacher_student.html"

        context['title'] = _('Categories')

        if self.request.is_ajax():
            if self.request.user.is_staff:
                self.template_name = "categories/home_admin_content.html"
            else:
                self.template_name = "categories/home_teacher_student_content.html"

        return self.response_class(request = self.request, template = self.template_name, context = context, using = self.template_engine, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        
        categories = self.get_queryset().order_by('name')
        context['categories'] = categories
        context['settings_menu_active'] = "settings_menu_active"

        return context

class CreateCategory(views.SuperuserRequiredMixin, HasRoleMixin, LogMixin, CreateView):
    log_component = 'category'
    log_action = 'create'
    log_resource = 'category'
    log_context = {}

    allowed_rules = ['system_admin']
    login_url = reverse_lazy('users:login')
    form_class = CategoryForm
    template_name = 'categories/create.html'
    success_url = reverse_lazy('categories:index')

    def get_initial(self):
        initial = super(CreateCategory, self).get_initial()

        if self.kwargs.get('slug'):
            category = get_object_or_404(Category, slug = self.kwargs['slug'])
            initial = initial.copy()

            initial['description'] = category.description
            initial['name'] = category.name
            initial['visible'] = category.visible
            initial['coordinators'] = category.coordinators.all()

            self.log_action = 'replicate'

            self.log_context['replicated_category_id'] = category.id
            self.log_context['replicated_category_name'] = category.name
            self.log_context['replicated_category_slug'] = category.slug

        return initial

    def get_context_data(self, **kwargs):
        context = super(CreateCategory, self).get_context_data(**kwargs)
        context['users_count'] = User.objects.all().count()
        context['switch'] = True

        if self.kwargs.get('slug'):
            context['title'] = _('Replicate Category')
        else:
            context['title'] = _('Create Category')

        if 'categories' in self.request.META.get('HTTP_REFERER'):
            context['template_extends'] = 'categories/list.html'
            context['settings_menu_active'] = "settings_menu_active"
        else:
            context['template_extends'] = 'subjects/list.html'

        return context

    def form_valid(self, form):
        self.object = form.save()
        
        self.log_context['category_id'] = self.object.id
        self.log_context['category_name'] = self.object.name
        self.log_context['category_slug'] = self.object.slug

        super(CreateCategory, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return super(CreateCategory, self).form_valid(form)

    def get_success_url(self):
    
        objeto = self.object.name
        messages.success(self.request, _('Category "%s" register successfully!')%(objeto))
        return reverse_lazy('categories:index')


class DeleteCategory(LogMixin, DeleteView):
    log_component = 'category'
    log_action = 'delete'
    log_resource = 'category'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Category
    template_name = 'categories/delete.html'

    def delete(self, request, *args, **kwargs):
        category = get_object_or_404(Category, slug = self.kwargs.get('slug'))
        subjects = Subject.objects.filter(category = category)
        
        if subjects.count() > 0:
            #objeto = category
            #messages.success(self.request, _('cannot delete Category "%s" ')%(objeto))
            return reverse_lazy('categories:index')
       
        return super(DeleteCategory, self).delete(self, request, *args, **kwargs)

    def get_success_url(self):
        self.log_context['category_id'] = self.object.id
        self.log_context['category_name'] = self.object.name
        self.log_context['category_slug'] = self.object.slug

        super(DeleteCategory, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        messages.success(self.request, _('Category removed successfully!'))
        return reverse_lazy('categories:index')


class UpdateCategory(LogMixin, UpdateView):
    log_component = 'category'
    log_action = 'update'
    log_resource = 'category'
    log_context = {}

    model = Category
    form_class = CategoryForm
    template_name = 'categories/update.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    def get_success_url(self):
        self.log_context['category_id'] = self.object.id
        self.log_context['category_name'] = self.object.name
        self.log_context['category_slug'] = self.object.slug

        super(UpdateCategory, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        objeto = self.object.name
        messages.success(self.request, _('Category "%s" updated successfully!')%(objeto))

        return reverse_lazy('categories:index')

    def get_context_data(self, **kwargs):
        context = super(UpdateCategory, self).get_context_data(**kwargs)
        context['title'] = _('Update Category')

        if 'categories' in self.request.META.get('HTTP_REFERER'):
            context['template_extends'] = 'categories/list.html'
            context['settings_menu_active'] = "settings_menu_active"
        else:
            context['template_extends'] = 'subjects/list.html'

        return context

@log_decorator_ajax('category', 'view', 'category')
def category_view_log(request, category):
    action = request.GET.get('action')

    if action == 'open':
        category = get_object_or_404(Category, id = category)

        log_context = {}
        log_context['category_id'] = category.id
        log_context['category_name'] = category.name
        log_context['category_slug'] = category.slug
        log_context['timestamp_start'] = str(int(time.time()))
        log_context['timestamp_end'] = '-1'

        request.log_context = log_context

        log_id = Log.objects.latest('id').id

        return JsonResponse({'message': 'ok', 'log_id': log_id})

    return JsonResponse({'message': 'ok'})
