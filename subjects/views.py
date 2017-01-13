
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, TemplateView
from categories.models import Category
from django.core.urlresolvers import reverse_lazy
from rolepermissions.verifications import has_role
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.mixins import LoginRequiredMixin

from rolepermissions.mixins import HasRoleMixin
from categories.forms import CategoryForm

from braces import views
from subjects.models import Subject

from log.mixins import LogMixin
from log.decorators import log_decorator_ajax
from log.models import Log

from .models import Tag
import time
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CreateSubjectForm
from .utils import has_student_profile, has_professor_profile, count_subjects
from users.models import User


class HomeView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'subjects/initial.html'
    context_object_name = 'subjects'
    paginate_by = 10    

    def get_queryset(self):
        if self.request.user.is_staff:
            subjects = Subject.objects.all().order_by("name")
        else:


            pk = self.request.user.pk

            subjects = Subject.objects.filter(students__pk=pk) | Subject.objects.filter(professor__pk=pk) | Subject.objects.filter(category__coordinators__pk=pk)
            

        return subjects

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['title'] = _('Home')
        context['show_buttons'] = True #So it shows subscribe and access buttons
       
        #bringing users
        tags = Tag.objects.all()
        context['tags'] = tags
        return context


class IndexView(LoginRequiredMixin, ListView):
    totals = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'subjects/list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        categories = Category.objects.all().order_by('name')

        self.totals['all_subjects'] = count_subjects(categories, self.request.user)
        self.totals['my_subjects'] = self.totals['all_subjects']

        if not self.request.user.is_staff:
            my_categories = [category for category in categories if self.request.user in category.coordinators.all() \
                        or has_professor_profile(self.request.user, category) or has_student_profile(self.request.user, category)] 
                        #So I remove all categories that doesn't have the possibility for the user to be on

            self.totals['my_subjects'] = count_subjects(my_categories, self.request.user, False)

            if not self.kwargs.get('option'):
                categories = my_categories

        return categories

    def render_to_response(self, context, **response_kwargs):
        if self.request.user.is_staff:
            context['page_template'] = "categories/home_admin_content.html"
        else:
            context['page_template'] = "categories/home_teacher_student.html"

        if self.request.is_ajax():
            if self.request.user.is_staff:
                self.template_name = "categories/home_admin_content.html"
            else:
                self.template_name = "categories/home_teacher_student_content.html"

        return self.response_class(request = self.request, template = self.template_name, context = context, using = self.template_engine, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['all'] = False
        context['title'] = _('My Subjects')

        context['show_buttons'] = True #So it shows subscribe and access buttons
        context['totals'] = self.totals
            
        if self.kwargs.get('option'):
            context['all'] = True
            context['title'] = _('All Subjects')

        context['subjects_menu_active'] = 'subjects_menu_active'

        return context

class SubjectCreateView(CreateView):
    model = Subject
    template_name = "subjects/create.html"

    login_url = reverse_lazy('users:login')
    form_class = CreateSubjectForm
    
    success_url = reverse_lazy('subject:index')

    def get_initial(self):
        initial = super(SubjectCreateView, self).get_initial()
        if self.kwargs.get('slug'): #when the user creates a subject
            initial['category'] = Category.objects.all().filter(slug=self.kwargs['slug'])

        if self.kwargs.get('subject_slug'): #when the user updates a subject
            subject = get_object_or_404(Subject, slug = self.kwargs['subject_slug'])
            initial = initial.copy()
            initial['category'] = subject.category
            initial['description'] = subject.description
            initial['name'] = subject.name
            initial['visible'] = subject.visible
            initial['professor'] = subject.professor.all()
            initial['tags'] = ", ".join(subject.tags.all().values_list("name", flat = True))
            initial['init_date'] = subject.init_date
            initial['end_date'] = subject.end_date
            initial['students'] = subject.students.all()
            initial['description_brief'] = subject.description_brief
        
        return initial

    def get_context_data(self, **kwargs):
        context = super(SubjectCreateView, self).get_context_data(**kwargs)
        context['title'] = _('Create Subject')
        if self.kwargs.get('slug'):
            context['slug'] = self.kwargs['slug']
        if self.kwargs.get('subject_slug'):
            subject = get_object_or_404(Subject, slug = self.kwargs['subject_slug'])
            context['slug'] = subject.category.slug
        context['subjects_menu_active'] = 'subjects_menu_active'
        
        return context

    def form_valid(self, form):
        
        self.object = form.save()
        if self.kwargs.get('slug'):
            self.object.category = Category.objects.get(slug=self.kwargs['slug'])
        if self.kwargs.get('subject_slug'):
            subject = get_object_or_404(Subject, slug = self.kwargs['subject_slug'])
            self.object.category = subject.category
        self.object.save()        

        return super(SubjectCreateView, self).form_valid(form)

    def get_success_url(self):
        if not self.object.category.visible:
            self.object.visible = False
            self.object.save()

        messages.success(self.request, _('Subject "%s" was registered on "%s" successfully!')%(self.object.name, self.object.category.name ))
        return reverse_lazy('subjects:index')

class SubjectUpdateView(LogMixin, UpdateView):
    model = Subject
    form_class = CreateSubjectForm
    template_name = 'subjects/update.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super(SubjectUpdateView, self).get_context_data(**kwargs)
        context['title'] = _('Update Subject')
        context['template_extends'] = 'categories/home.html'
        context['subjects_menu_active'] = 'subjects_menu_active'
        
        return context

    def get_success_url(self):
        if not self.object.category.visible:
            self.object.visible = False
            self.object.save()
        
        messages.success(self.request, _('Subject "%s" was updated on "%s" successfully!')%(self.object.name, self.object.category.name ))
        return reverse_lazy('subjects:index')

class SubjectDeleteView(LoginRequiredMixin, LogMixin, DeleteView):
   
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Subject
    template_name = 'subjects/delete.html'

    def dispatch(self, *args, **kwargs):
        
        return super(SubjectDeleteView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.students.all().count() > 0:
            messages.error(self.request, _("Subject can't be removed. The subject still possess students and learning objects associated"))
            
            return JsonResponse({'error':True,'url':reverse_lazy('subjects:index')})
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    def get_context_data(self, **kwargs):
        context = super(SubjectDeleteView, self).get_context_data(**kwargs)
        subject = get_object_or_404(Subject, slug = self.kwargs.get('slug'))
        context['subject'] = subject

      
        if (self.request.GET.get('view') == 'index'):
            context['index'] = True
        else:
            context['index'] = False

        return context

    def get_success_url(self):
        
        messages.success(self.request, _('Subject removed successfully!'))
        
        return reverse_lazy('subjects:index')


class SubjectDetailView(TemplateView):
    model = Subject
    template_name = 'subjects/view.html'

    def get_context_data(self, **kwargs):
        context = super(SubjectDetailView, self).get_context_data(**kwargs)
        context['subject'] = get_object_or_404(Subject, slug = self.kwargs.get('slug'))
        context['show_buttons'] = False #So it doesn't show subscribe and access buttons
        

        return context

def subscribe_subject(request, subject_slug):
    subject = get_object_or_404(Subject, slug= subject_slug)
    subject.students.add(request.user)
    subject.save()

    messages.success(self.request, _('Subcribed "%s" was updated on "%s" successfully!')%(self.object.name, self.object.category.name ))
    return reverse_lazy('subjects:index')


