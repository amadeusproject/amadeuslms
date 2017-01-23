
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, TemplateView, DetailView
from categories.models import Category
from django.core.urlresolvers import reverse_lazy
from rolepermissions.verifications import has_role
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
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
from .utils import has_student_profile, has_professor_profile, count_subjects, get_category_page
from users.models import User


class HomeView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'subjects/initial.html'
    context_object_name = 'subjects'
    paginate_by = 10
    total = 0    

    def get_queryset(self):
        if self.request.user.is_staff:
            subjects = Subject.objects.all().order_by("name")
        else:
            pk = self.request.user.pk

            subjects = Subject.objects.filter(Q(students__pk=pk) | Q(professor__pk=pk) | Q(category__coordinators__pk=pk)).distinct()
        
        self.total = len(subjects)

        return subjects

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['title'] = _('Home')
        context['show_buttons'] = True #So it shows subscribe and access buttons
       
        #bringing users
        tags = Tag.objects.all()
        context['tags'] = tags
        context['total_subs'] = self.total

        return context


class IndexView(LoginRequiredMixin, ListView):
    totals = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'subjects/list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):        
        if self.request.user.is_staff:
            categories = Category.objects.all().order_by('name')
        else:
            pk = self.request.user.pk
            
            categories = Category.objects.filter(Q(coordinators__pk = pk) | Q(visible=True) ).distinct().order_by('name')
        
        self.totals['all_subjects'] = count_subjects(self.request.user)
        
        self.totals['my_subjects'] = self.totals['all_subjects']

        if not self.request.user.is_staff:
            
            #my_categories = Category.objects.filter(Q(coordinators__pk=pk) | Q(subject_professor__pk=pk) | Q())
            my_categories = [category for category in categories if self.request.user in category.coordinators.all() \
                        or has_professor_profile(self.request.user, category) or has_student_profile(self.request.user, category)] 
                        #So I remove all categories that doesn't have the possibility for the user to be on
           
            self.totals['my_subjects'] = count_subjects(self.request.user, False)
            
            if not self.kwargs.get('option'):
                categories = my_categories

        return categories

    def paginate_queryset(self, queryset, page_size): 
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        
        page_kwarg = self.page_kwarg
        
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        
        if self.kwargs.get('slug'):
            categories = queryset

            paginator = Paginator(categories, self.paginate_by)

            page = get_category_page(categories, self.kwargs.get('slug'), self.paginate_by)
        
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_("Page is not 'last', nor can it be converted to an int."))
        
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })

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

        if self.kwargs.get('slug'):
            context['cat_slug'] = self.kwargs.get('slug')

        context['subjects_menu_active'] = 'subjects_menu_active'

        return context

class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    template_name = "subjects/create.html"

    login_url = reverse_lazy('users:login')
    redirect_field_name = 'next'
    form_class = CreateSubjectForm
    
    success_url = reverse_lazy('subject:index')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = user.pk 
        if kwargs.get('subject_slug'):
            subject = Subject.objects.filter((Q(professor__pk=pk) | Q(category__coordinators__pk=pk)) & Q(slug = kwargs.get('subject_slug')))
            if not user.is_staff:
                if subject.count() == 0:
                    if request.META.get('HTTP_REFERER'):
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    else:
                        return redirect('subjects:index')
    

        if kwargs.get('slug'):
            subject = Subject.objects.filter((Q(professor__pk=pk) | Q(category__coordinators__pk=pk)) & Q(slug = kwargs.get('slug')))
            if not user.is_staff:
                if subject.count() == 0:
                        if request.META.get('HTTP_REFERER'):
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                        else:
                            return redirect('subjects:index')               
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
   

    def get_initial(self):
        initial = super(SubjectCreateView, self).get_initial()
        if self.kwargs.get('slug'): #when the user creates a subject
            initial['category'] = Category.objects.all().filter(slug=self.kwargs['slug'])

        if self.kwargs.get('subject_slug'): #when the user replicate a subject
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
            context['title'] = _('Replicate Subject')

            subject = get_object_or_404(Subject, slug = self.kwargs['subject_slug'])
            
            context['slug'] = subject.category.slug
            context['replicate'] = True

            context['subject'] = subject
        

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

class SubjectUpdateView(LoginRequiredMixin, LogMixin, UpdateView):
    model = Subject
    form_class = CreateSubjectForm
    template_name = 'subjects/update.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        
        pk = user.pk

        subject = Subject.objects.filter((Q(professor__pk=pk) | Q(category__coordinators__pk=pk)) & Q(slug = kwargs.get('slug')))
        if not user.is_staff:
            if subject.count() == 0:
                if request.META.get('HTTP_REFERER'):
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    return redirect('subjects:index')

        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

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

    def dispatch(self,request, *args, **kwargs):
        user = self.request.user
        
        pk = user.pk

        subject = Subject.objects.filter((Q(professor__pk=pk) | Q(category__coordinators__pk=pk)) & Q(slug = kwargs.get('slug')))
        if not user.is_staff:
            if subject.count() == 0:
                if request.META.get('HTTP_REFERER'):
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    return redirect('subjects:index')
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


        
        messages.success(self.request, _('Subject "%s" removed successfully!')%(self.object.name))
        
        return reverse_lazy('subjects:index')


class SubjectDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    model = Subject
    template_name = 'subjects/view.html'
    context_object_name = 'subject'

    def dispatch(self, request, *args,**kwargs):
        user = request.user
        pk = user.pk
        if kwargs.get('slug') and not user.is_staff:
            subject = get_object_or_404(Subject, slug = kwargs.get('slug'))

            subject = Subject.objects.filter((Q(students__pk=pk) | Q(professor__pk=pk) | Q(category__coordinators__pk=pk)) & Q(slug = kwargs.get('slug')))
            
            if subject.count() == 0:
                if request.META.get('HTTP_REFERER'):
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    return redirect('subjects:home')
                            
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SubjectDetailView, self).get_context_data(**kwargs)
        context['title'] = self.object.name

        resources = self.request.session.get('resources', None)

        if resources:
            context['resource_new_page'] = resources['new_page']
            context['resource_new_page_url'] = resources['new_page_url']

            self.request.session['resources'] = None

        return context


class SubjectSubscribeView(LoginRequiredMixin, TemplateView):

    template_name = 'subjects/subscribe.html'

    def get_context_data(self, **kwargs):
        context = super(SubjectSubscribeView, self).get_context_data(**kwargs)
        context['subject'] = get_object_or_404(Subject, slug= kwargs.get('slug'))

        return context

    def post(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug= kwargs.get('slug'))
        if subject.subscribe_end < datetime.datetime.today().date():
            messages.error(self.request, _('Subscription date is due!'))
        else:
            subject.students.add(request.user)
            subject.save()
            messages.success(self.request, _('Subscription was successfull!'))
       
        return JsonResponse({'url':reverse_lazy('subjects:index')})


class SubjectSearchView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:login")
    template_name = 'subjects/list_search.html'
    context_object_name = 'subjects'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        tags =  request.GET.get('search')
        tags = tags.split(" ")

        if tags[0] == '':
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
   
    def get_queryset(self):
        
        tags = self.request.GET.get('search')

        self.tags = tags
        tags = tags.split(" ")
       
       
        subjects = Subject.objects.filter(tags__name__in=tags)
        #pk = self.request.user.pk
        #my_subjects = Subject.objects.filter(Q(students__pk=pk) | Q(professor__pk=pk) | Q(category__coordinators__pk=pk) & Q(tags__name__in=tags) ).distinct()
        
        self.totals = {'all_subjects': subjects.count(), 'my_subjects': subjects.count()}
        #if self.kwargs.get('option'):
        #    subjects = my_subjects
        return subjects
   
    def get_context_data(self, **kwargs):
        context = super(SubjectSearchView, self).get_context_data(**kwargs)
        
        context['tags'] = self.tags
        context['all'] = False
        context['title'] = _('Subjects')

        context['show_buttons'] = True #So it shows subscribe and access buttons
        context['totals'] = self.totals
        
        if self.kwargs.get('option'):
            context['all'] = True
            context['title'] = _('Subjects')

        context['subjects_menu_active'] = 'subjects_menu_active'

        return context
   

