
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
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

from .models import Marker
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CreateSubjectForm
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
            subjects = Subject.objects.all()
        else:
            subjects = Subject.objects.all()
            subjects = [subject for subject in subjects if self.request.user in subject.students.all() or self.request.user in subject.professor.all() or self.request.user in subject.category.coordinators.all()]

           
        paginator = Paginator(subjects, 10)


        return subjects

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['title'] = _('Home')
       
        #bringing users
        markers = Marker.objects.all()
        context['markers'] = markers
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

                for category in categories:
                    category.subjects = Subject.objects.filter(category= category)

                categories = [category for category in categories if category.subjects.count() > 0 or self.request.user in category.coordinators.all()] 
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
        initial['category'] = Category.objects.all().filter(slug=self.kwargs['slug'])
        
        return initial

    def get_context_data(self, **kwargs):
        context = super(SubjectCreateView, self).get_context_data(**kwargs)
        context['title'] = _('Create Subject')
        context['slug'] = self.kwargs['slug']
        context['subjects_menu_active'] = 'subjects_menu_active'
        
        return context

    def form_valid(self, form):
        
        self.object = form.save()
        self.object.category = Category.objects.get(slug=self.kwargs['slug'])
        self.object.save()
        

        return super(SubjectCreateView, self).form_valid(form)

    def get_success_url(self):
        objeto = self.object.name
        
        messages.success(self.request, _('Subject "%s" was registered on "%s" successfully!')%(objeto, self.kwargs['slug']))
        return reverse_lazy('subjects:index')


