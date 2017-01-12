
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, TemplateView
from categories.models import Category
from django.core.urlresolvers import reverse_lazy
from rolepermissions.verifications import has_role

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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CreateSubjectForm
from .utils import has_student_profile, has_professor_profile
from users.models import User


class HomeView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    queryset = Subject.objects.all()
    template_name = 'subjects/initial.html'
    context_object_name = 'subjects'
    paginate_by = 10    

    def get_queryset(self):
        if self.request.user.is_staff:
            subjects = Subject.objects.all().order_by("name")
        else:
            subjects = Subject.objects.all().order_by("name")
            subjects = [subject for subject in subjects if self.request.user in subject.students.all() or self.request.user in subject.professor.all() or self.request.user in subject.category.coordinators.all()]

     

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

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    queryset = Category.objects.all()
    template_name = 'subjects/list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        categories = Category.objects.all().order_by('name')

        if not self.request.user.is_staff:
            if not self.kwargs.get('option'):
                categories = Category.objects.all()

                categories = [category for category in categories if self.request.user in category.coordinators.all() \
                    or has_professor_profile(self.request.user, category) or has_student_profile(self.request.user, category)] 
                #So I remove all categories that doesn't have the possibility for the user to be on

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
            initial['tags'] = subject.tags.all()
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

    def get_context_data(self, **kwargs):
        context = super(SubjectDeleteView, self).get_context_data(**kwargs)
        context['subject'] = get_object_or_404(Subject, slug = self.kwargs.get('slug'))

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


