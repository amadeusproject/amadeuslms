
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
from random import shuffle
from rolepermissions.mixins import HasRoleMixin
from categories.forms import CategoryForm

from braces import views
from subjects.models import Subject

from log.mixins import LogMixin
from log.decorators import log_decorator_ajax
from log.models import Log
from itertools import chain
from .models import Tag
import time
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CreateSubjectForm, UpdateSubjectForm
from .utils import has_student_profile, has_professor_profile, count_subjects, get_category_page
from users.models import User
from topics.models import Resource

from amadeus.permissions import has_category_permissions, has_subject_permissions, has_subject_view_permissions

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
        
        self.total = subjects.count()

        return subjects

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['title'] = _('Home')
        context['show_buttons'] = True #So it shows subscribe and access buttons
       
        #bringing users
        tag_amount = 50
        tags = Tag.objects.all()
        tags_list = []
        for tag in tags:
            if Resource.objects.filter(tags__pk=tag.pk).count() > 0 and len(tags_list) <= tag_amount:
                tags_list.append((tag.name, Subject.objects.filter(tags__pk = tag.pk).count()))
                tags_list.sort(key= lambda x: x[1], reverse=True) #sort by value
                
            elif len(tags_list) > tag_amount:
                count = Subject.objects.filter(tags__pk = tag.pk).count()
                if count > tags_list[tag_amount][1]:
                    tags_list[tag_amount - 1] = (tag.name, count)
                    tags_list.sort(key = lambda x: x[1], reverse=True)

       
        i = 0
        tags = []

        for item in tags_list:
            if i < tag_amount/10:
                tags.append((item[0], 0))
            elif i < tag_amount/2:
                tags.append((item[0], 1))
            else:
                tags.append((item[0], 2))
            i += 1
        shuffle(tags)

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
        self.totals['all_subjects'] = count_subjects(self.request.user)
        
        self.totals['my_subjects'] = self.totals['all_subjects']
        
        if self.request.user.is_staff:
            categories = Category.objects.all().order_by('name')
        else:
            pk = self.request.user.pk
            
            self.totals['my_subjects'] = count_subjects(self.request.user, False)
        
            if not self.kwargs.get('option'):
                my_categories = Category.objects.filter(Q(coordinators__pk=pk) | Q(subject_category__professor__pk=pk) | Q(subject_category__students__pk = pk, visible = True)).distinct().order_by('name')
                
                categories = my_categories
            else:
                categories = Category.objects.filter(Q(coordinators__pk = pk) | Q(visible=True) ).distinct().order_by('name')
        
        #if not self.request.user.is_staff:
                        
                #my_categories = [category for category in categories if self.request.user in category.coordinators.all() \
                        #or has_professor_profile(self.request.user, category) or has_student_profile(self.request.user, category)] 
                        #So I remove all categories that doesn't have the possibility for the user to be on
           

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

class GetSubjectList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'subjects/_list.html'
    model = Subject
    context_object_name = 'subjects'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug = slug)

        return category.subject_category.all()

    def get_context_data(self, **kwargs):
        context = super(GetSubjectList, self).get_context_data(**kwargs)

        context['show_buttons'] = True #So it shows subscribe and access buttons

        if 'all' in self.request.META.get('HTTP_REFERER'):
            context['all'] = True

        return context

class SubjectCreateView(LoginRequiredMixin, LogMixin, CreateView):
    log_component = 'subject'
    log_action = 'create'
    log_resource = 'subject'
    log_context = {}

    model = Subject
    template_name = "subjects/create.html"

    login_url = reverse_lazy('users:login')
    redirect_field_name = 'next'
    form_class = CreateSubjectForm
    
    success_url = reverse_lazy('subject:index')

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('subject_slug'):
            subject = get_object_or_404(Subject, slug = kwargs.get('subject_slug', ''))
            
            if not has_category_permissions(request.user, subject.category):
                return redirect(reverse_lazy('subjects:home'))

        if kwargs.get('slug'):
            category = get_object_or_404(Category, slug = kwargs.get('slug', ''))

            if not has_category_permissions(request.user, category):
                return redirect(reverse_lazy('subjects:home'))
            
        return super(SubjectCreateView, self).dispatch(request, *args, **kwargs)
   

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
        
            self.log_action = 'replicate'

            self.log_context['replicated_subject_id'] = subject.id
            self.log_context['replicated_subject_name'] = subject.name
            self.log_context['replicated_subject_slug'] = subject.slug

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

        self.log_context['category_id'] = self.object.category.id
        self.log_context['category_name'] = self.object.category.name
        self.log_context['category_slug'] = self.object.category.slug
        self.log_context['subject_id'] = self.object.id
        self.log_context['subject_name'] = self.object.name
        self.log_context['subject_slug'] = self.object.slug

        super(SubjectCreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)        

        return super(SubjectCreateView, self).form_valid(form)

    def get_success_url(self):
        if not self.object.category.visible:
            self.object.visible = False
            self.object.save()

        messages.success(self.request, _('The Subject "%s" was registered on "%s" Category successfully!')%(self.object.name, self.object.category.name ))
        return reverse_lazy('subjects:index')

class SubjectUpdateView(LoginRequiredMixin, LogMixin, UpdateView):
    log_component = 'subject'
    log_action = 'update'
    log_resource = 'subject'
    log_context = {}

    model = Subject
    form_class = UpdateSubjectForm
    template_name = 'subjects/update.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug = kwargs.get('slug', ''))
        
        if not has_subject_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SubjectUpdateView, self).dispatch(request, *args, **kwargs)

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

        self.log_context['category_id'] = self.object.category.id
        self.log_context['category_name'] = self.object.category.name
        self.log_context['category_slug'] = self.object.category.slug
        self.log_context['subject_id'] = self.object.id
        self.log_context['subject_name'] = self.object.name
        self.log_context['subject_slug'] = self.object.slug

        super(SubjectUpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)
        
        messages.success(self.request, _('The Subject "%s" was updated on "%s" Category successfully!')%(self.object.name, self.object.category.name ))
       
        return reverse_lazy('subjects:index')

class SubjectDeleteView(LoginRequiredMixin, LogMixin, DeleteView):
    log_component = 'subject'
    log_action = 'delete'
    log_resource = 'subject'
    log_context = {}
   
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Subject
    template_name = 'subjects/delete.html'

    def dispatch(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug = kwargs.get('slug', ''))
        
        if not has_subject_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SubjectDeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.students.count() > 0:
            messages.error(self.request, _("Subject can't be removed. The subject still possess students and learning objects associated"))
            return JsonResponse({'error':True,'url':reverse_lazy('subjects:index')})
        for topic in self.object.topic_subject.all():
            if topic.resource_topic.count() > 0:
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
        self.log_context['category_id'] = self.object.category.id
        self.log_context['category_name'] = self.object.category.name
        self.log_context['category_slug'] = self.object.category.slug
        self.log_context['subject_id'] = self.object.id
        self.log_context['subject_name'] = self.object.name
        self.log_context['subject_slug'] = self.object.slug

        super(SubjectDeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        
        messages.success(self.request, _('Subject "%s" removed successfully!')%(self.object.name))
        
        return reverse_lazy('subjects:index')


class SubjectDetailView(LoginRequiredMixin, LogMixin, DetailView):
    log_component = 'subject'
    log_action = 'access'
    log_resource = 'subject'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    model = Subject
    template_name = 'subjects/view.html'
    context_object_name = 'subject'

    def dispatch(self, request, *args,**kwargs):
        subject = get_object_or_404(Subject, slug = kwargs.get('slug', ''))

        if not has_subject_view_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SubjectDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SubjectDetailView, self).get_context_data(**kwargs)
        context['title'] = self.object.name

        resources = self.request.session.get('resources', None)

        if resources:
            context['resource_new_page'] = resources['new_page']
            context['resource_new_page_url'] = resources['new_page_url']

            self.request.session['resources'] = None

        if self.kwargs.get('topic_slug'):
            context['topic_slug'] = self.kwargs.get('topic_slug')

        self.log_context['category_id'] = self.object.category.id
        self.log_context['category_name'] = self.object.category.name
        self.log_context['category_slug'] = self.object.category.slug
        self.log_context['subject_id'] = self.object.id
        self.log_context['subject_name'] = self.object.name
        self.log_context['subject_slug'] = self.object.slug
        self.log_context['timestamp_start'] = str(int(time.time()))

        super(SubjectDetailView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        self.request.session['log_id'] = Log.objects.latest('id').id

        return context

class SubjectSubscribeView(LoginRequiredMixin, LogMixin, TemplateView):
    log_component = 'subject'
    log_action = 'subscribe'
    log_resource = 'subject'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

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
            self.log_context['category_id'] = subject.category.id
            self.log_context['category_name'] = subject.category.name
            self.log_context['category_slug'] = subject.category.slug
            self.log_context['subject_id'] = subject.id
            self.log_context['subject_name'] = subject.name
            self.log_context['subject_slug'] = subject.slug

            super(SubjectSubscribeView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

            subject.students.add(request.user)
            subject.save()
            messages.success(self.request, _('Subscription was successfull!'))
       
        return JsonResponse({'url':reverse_lazy('subjects:index')})


class SubjectSearchView(LoginRequiredMixin, LogMixin, ListView):
    log_component = 'subject'
    log_action = 'search'
    log_resource = 'subject/resources'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

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
        q = Q()
        for tag in tags:
            for word in tag.split(' '):
                q = q | Q(tags__name__unaccent__iexact=word  )
        
        subjects = Subject.objects.filter(q).distinct()
        self.resources = Resource.objects.select_related('link', 'filelink', 'webpage', 'ytvideo', 'pdffile').filter(q ).distinct()

        
        self.totals = {'resources': self.resources.count(), 'my_subjects': subjects.count()}
       
        option = self.kwargs.get('option')
        if option and option == 'resources':
            return self.resources
        return subjects
   
    def get_context_data(self, **kwargs):
        context = super(SubjectSearchView, self).get_context_data(**kwargs)
        
        if self.totals['resources'] == 0 and self.totals['my_subjects'] == 0:
            context['empty'] = True
        context['tags'] = self.tags
        context['all'] = False
        context['title'] = _('Subjects')

        context['show_buttons'] = True #So it shows subscribe and access buttons
        context['totals'] = self.totals
        option = self.kwargs.get('option')
        if option and option == 'resources':
            context['all'] = True
            context['title'] = _('Resources')
            context['resources'] = self.resources

        context['subjects_menu_active'] = ''

        self.log_context['search_for'] = self.tags
        super(SubjectSearchView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return context
   
@log_decorator_ajax('subject', 'view', 'subject')
def subject_view_log(request, subject):
    action = request.GET.get('action')

    if action == 'open':
        subject = get_object_or_404(Subject, id = subject)

        log_context = {}
        log_context['category_id'] = subject.category.id
        log_context['category_name'] = subject.category.name
        log_context['category_slug'] = subject.category.slug
        log_context['subject_id'] = subject.id
        log_context['subject_name'] = subject.name
        log_context['subject_slug'] = subject.slug
        log_context['timestamp_start'] = str(int(time.time()))
        log_context['timestamp_end'] = '-1'

        request.log_context = log_context

        log_id = Log.objects.latest('id').id

        return JsonResponse({'message': 'ok', 'log_id': log_id})

    return JsonResponse({'message': 'ok'})

