""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from .models import Category
from django.core.urlresolvers import reverse_lazy
from rolepermissions.verifications import has_role
from django.db.models import Q
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

from topics.models import Topic, Resource
from users.models import User

class IndexView(LoginRequiredMixin, views.StaffuserRequiredMixin, ListView):

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Category

    template_name = 'categories/list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        categories = Category.objects.all().order_by('name')

        return categories

    def render_to_response(self, context, **response_kwargs):
        if self.request.user.is_staff:
            context['page_template'] = "categories/home_admin_content.html"
        else:
            context['page_template'] = "categories/home_teacher_student.html"

        context['title'] = _('Categories')

        if self.request.is_ajax():
            if self.request.user.is_staff:
                self.template_name = "categories/home_admin_content.html"
           

        return self.response_class(request = self.request, template = self.template_name, context = context, using = self.template_engine, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        
        context['settings_menu_active'] = "settings_menu_active"

        return context

class CreateCategory(LoginRequiredMixin, views.StaffuserRequiredMixin, LogMixin, CreateView):
    log_component = 'category'
    log_action = 'create'
    log_resource = 'category'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    
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
            context['subjects_menu_active'] = 'subjects_menu_active';

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

class DeleteCategory(LoginRequiredMixin, LogMixin, DeleteView):
    log_component = 'category'
    log_action = 'delete'
    log_resource = 'category'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    model = Category
    template_name = 'categories/delete.html'

    def dispatch(self, request, *args, **kwargs):
        pk = request.user.pk

        if not request.user.is_staff:
            category = Category.objects.filter(Q(coordinators__pk = pk) & Q(slug = kwargs['slug']))
            if category.count() == 0:
                if request.META.get('HTTP_REFERER'):
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    return redirect('subjects:index')
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        category = get_object_or_404(Category, slug = self.kwargs.get('slug'))
        subjects = Subject.objects.filter(category = category)
        
        if subjects.count() > 0:
            messages.error(self.request, _('The category cannot be removed, it contains one or more virtual enviroments attach.'))
            
            return redirect(self.request.META.get('HTTP_REFERER'))
       
        return super(DeleteCategory, self).delete(self, request, *args, **kwargs)

    def get_success_url(self):
        self.log_context['category_id'] = self.object.id
        self.log_context['category_name'] = self.object.name
        self.log_context['category_slug'] = self.object.slug

        super(DeleteCategory, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        messages.success(self.request, _('Category "%s" removed successfully!')%(self.object.name))
        
        return self.request.META.get('HTTP_REFERER')

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

        #url to return
        return_url = self.log_context['return_url']
        self.log_context.pop('return_url', None)

        super(UpdateCategory, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        messages.success(self.request, _('Category "%s" updated successfully!')%(self.object.name))

        return return_url

    def form_valid(self, form):
        category = form.save()

        if not category.visible:
            category.subject_category.all().update(visible = False)
            Topic.objects.filter(subject__category = category, repository = False).update(visible = False)
            Resource.objects.filter(topic__subject__category = category, topic__repository = False).update(visible = False)

        return super(UpdateCategory, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UpdateCategory, self).get_context_data(**kwargs)
        context['title'] = _('Update Category')

        if self.request.method == 'GET':
            self.log_context['return_url'] = self.request.META.get('HTTP_REFERER')

        if 'categories' in self.request.META.get('HTTP_REFERER'):
            context['template_extends'] = 'categories/list.html'
            context['settings_menu_active'] = "settings_menu_active"
        else:
            context['template_extends'] = 'subjects/list.html'
            context['subjects_menu_active'] = 'subjects_menu_active'

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
