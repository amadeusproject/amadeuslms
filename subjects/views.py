""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, TemplateView, DetailView
from categories.models import Category
from django.core.urlresolvers import reverse_lazy
from rolepermissions.verifications import has_role
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.mixins import LoginRequiredMixin
from random import shuffle
from rolepermissions.mixins import HasRoleMixin
from categories.forms import CategoryForm
import operator
from braces import views
from subjects.models import Subject
from django.contrib.auth.decorators import login_required
from collections import namedtuple

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
from topics.models import Topic, Resource
from news.models import News

import os
import zipfile
import json
from io import BytesIO
from itertools import chain
from django.core import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from users.serializers import UserBackupSerializer
from bulletin.serializers import SimpleBulletinSerializer, CompleteBulletinSerializer
from bulletin.models import Bulletin
from file_link.serializers import SimpleFileLinkSerializer, CompleteFileLinkSerializer
from file_link.models import FileLink
from goals.serializers import SimpleGoalSerializer, CompleteGoalSerializer
from goals.models import Goals
from links.serializers import SimpleLinkSerializer, CompleteLinkSerializer
from links.models import Link
from pdf_file.serializers import SimplePDFFileSerializer, CompletePDFFileSerializer
from pdf_file.models import PDFFile
from youtube_video.serializers import SimpleYTVideoSerializer, CompleteYTVideoSerializer
from youtube_video.models import YTVideo
from webpage.serializers import SimpleWebpageSerializer, CompleteWebpageSerializer
from webpage.models import Webpage
from webconference.serializers import SimpleWebconferenceSerializer, CompleteWebconferenceSerializer
from webconference.models import Webconference

from amadeus.permissions import has_category_permissions, has_subject_permissions, has_subject_view_permissions, has_resource_permissions

class HomeView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'subjects/home.html'
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
        context['news'] = News.objects.all()

        #bringing users
        tag_amount = 50
        tags = Tag.objects.all()
        tags_list = []
        for tag in tags:
            if len(tags_list) <= tag_amount:
                if Resource.objects.filter(tags__pk=tag.pk, students__pk = self.request.user.pk).count() > 0 or Subject.objects.filter(tags__pk = tag.pk).count() > 0:
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
            initial['category'] = Category.objects.filter(slug=self.kwargs['slug'])
            # print (initial)
            # initial['professor'] = User.objects.all()

        if self.kwargs.get('subject_slug'): #when the user replicate a subject
            subject = get_object_or_404(Subject, slug = self.kwargs['subject_slug'])
            initial = initial.copy()
            initial['category'] = Category.objects.filter(slug = subject.category.slug)
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
        try:
            students_selected = context['form'].cleaned_data['students'].values_list('id',flat=True)
            professors_selected = context['form'].cleaned_data['professor'].values_list('id',flat=True)
            context['form'].fields['professor'].queryset = context['form'].fields['professor'].queryset.exclude(id__in=students_selected)
            context['form'].fields['students'].queryset = context['form'].fields['students'].queryset.exclude(id__in=professors_selected)
        except AttributeError:
            pass
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
        self.subject = get_object_or_404(Subject, slug = kwargs.get('slug', ''))

        if not has_subject_permissions(request.user, self.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SubjectUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SubjectUpdateView, self).get_context_data(**kwargs)
        try:
            students_selected = context['form'].cleaned_data['students'].values_list('id',flat=True)
            professors_selected = context['form'].cleaned_data['professor'].values_list('id',flat=True)
        except AttributeError:
            students_selected = self.subject.students.all().values_list('id',flat=True)
            professors_selected = self.subject.professor.all().values_list('id',flat=True)

        context['form'].fields['professor'].queryset = context['form'].fields['professor'].queryset.exclude(id__in=students_selected)
        context['form'].fields['students'].queryset = context['form'].fields['students'].queryset.exclude(id__in=professors_selected)
        context['title'] = _('Update Subject')
        context['template_extends'] = 'categories/home.html'
        context['subjects_menu_active'] = 'subjects_menu_active'
        context['subject_data'] = get_object_or_404(Subject, slug = self.kwargs.get('slug', ''))

        return context

    def get_success_url(self):
        if not self.object.category.visible:
            self.object.visible = False
            self.object.save()

        if not self.object.visible:
            Topic.objects.filter(subject = self.object, repository = False).update(visible = False)
            Resource.objects.filter(topic__subject = self.object, topic__repository = False).update(visible = False)

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


    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if not (self.request.GET.get('view') == 'index'): #It still falling all the time into this if, I need to fix this
            return self.ajax_success()
        return HttpResponseRedirect(self.get_success_url())

    def ajax_success(self):
        self.log_context['category_id'] = self.object.category.id
        self.log_context['category_name'] = self.object.category.name
        self.log_context['category_slug'] = self.object.category.slug
        self.log_context['subject_id'] = self.object.id
        self.log_context['subject_name'] = self.object.name
        self.log_context['subject_slug'] = self.object.slug

        super(SubjectDeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        messages.success(self.request, _('Subject "%s" removed successfully!')%(self.object.name))

        return JsonResponse({'url':reverse_lazy('subjects:index')})


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

    def post(self, *args, **kwargs):

        return self.delete(*args, **kwargs)

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

        sub = self.kwargs.get('slug', '')

        status_query = "SELECT CASE WHEN action = 'logout' AND EXTRACT(EPOCH FROM(NOW() - datetime::timestamp)) < 1200 THEN 2 WHEN action = 'logout' AND EXTRACT(EPOCH FROM(NOW() - datetime::timestamp)) >= 1200 THEN 1 ELSE 0 END FROM log_log WHERE log_log.user_id = users_user.id ORDER BY datetime DESC LIMIT 1"

        expire_time = settings.SESSION_SECURITY_EXPIRE_AFTER

        context['participants'] = User.objects.filter(
            Q(subject_student__slug = sub) |
            Q(professors__slug = sub)
            ).extra(select = {'status': status_query}, select_params=(expire_time, expire_time,),).distinct().order_by('status', 'social_name','username').exclude(email = self.request.user.email)

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

        if subject.subscribe_end <= datetime.datetime.today().date():
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

        return redirect(reverse_lazy('subjects:view',kwargs={"slug": subject.slug}))


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

        return super(SubjectSearchView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):

        tags = self.request.GET.get('search')

        self.tags = tags
        tags = tags.split(" ")
        q = Q()
        for tag in tags:
            for word in tag.split(' '):
                q = q | Q(tags__name__unaccent__iexact=word  )

        subjects = Subject.objects.filter(q).distinct()

        self.resources = Resource.objects.select_related('link', 'filelink', 'webpage', 'ytvideo', 'pdffile').filter(q).distinct()
        self.resources = [resource.id for resource in self.resources if has_resource_permissions(self.request.user, resource)]
        self.resources = Resource.objects.select_related('link', 'filelink', 'webpage', 'ytvideo', 'pdffile').filter(id__in = self.resources)

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



""" BACKUP / RESTORE SECTION  """
class Backup(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'subjects/backup.html'
    model = Subject
    context_object_name = 'topics'

    def dispatch(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug = kwargs.get('slug', ''))

        if not has_subject_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(Backup, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        topics = Topic.objects.filter(subject__slug = slug)

        return topics

    def get_context_data(self, **kwargs):
        context = super(Backup, self).get_context_data(**kwargs)

        subject = get_object_or_404(Subject, slug = self.kwargs.get('slug', ''))
        
        context['title'] = _('%s - Backup')%(str(subject))
        context['subject'] = subject

        return context

@login_required
def realize_backup(request, subject):
    resources_ids = request.POST.getlist("resource[]")
    participants = request.POST.get('participants', False)

    resource_files_subdir = "files"
    zip_filename = "backup.zip"

    s = BytesIO()

    zf = zipfile.ZipFile(s, "w", compression = zipfile.ZIP_DEFLATED)

    bulletins = Bulletin.objects.filter(id__in = resources_ids)
    webpages = Webpage.objects.filter(id__in = resources_ids)
    ytvideos = YTVideo.objects.filter(id__in = resources_ids)
    filelinks = FileLink.objects.filter(id__in = resources_ids)
    links = Link.objects.filter(id__in = resources_ids)
    pdffiles = PDFFile.objects.filter(id__in = resources_ids)
    goals = Goals.objects.filter(id__in = resources_ids)
    webconferences = Webconference.objects.filter(id__in = resources_ids)


    for filelink in filelinks:
        if bool(filelink.file_content):
            if os.path.exists(filelink.file_content.path):
                fdir, fname = os.path.split(filelink.file_content.path)
                zip_path = os.path.join(resource_files_subdir, fname)

                # Add file, at correct path
                zf.write(filelink.file_content.path, zip_path)

    for pdffile in pdffiles:
        if bool(pdffile.file):
            if os.path.exists(pdffile.file.path):
                fdir, fname = os.path.split(pdffile.file.path)
                zip_path = os.path.join(resource_files_subdir, fname)

                # Add file, at correct path
                zf.write(pdffile.file.path, zip_path)

    for bulletin in bulletins:
        if bool(bulletin.file_content):
            if os.path.exists(bulletin.file_content.path):
                fdir, fname = os.path.split(bulletin.file_content.path)
                zip_path = os.path.join(os.path.join("bulletin", "goals"), fname)

                # Add file, at correct path
                zf.write(bulletin.file_content.path, zip_path)

        if bool(bulletin.indicators):
            if os.path.exists(bulletin.indicators.path):
                fdir, fname = os.path.split(bulletin.indicators.path)
                zip_path = os.path.join(os.path.join("bulletin", "indicators"), fname)

                # Add file, at correct path
                zf.write(bulletin.indicators.path, zip_path)

    file = open("backup.json", "w")

    data_list = []

    if participants:
        participants = User.objects.filter(subject_student__slug = subject)

        for user in participants:
            if bool(user.image):
                if os.path.exists(user.image.path):
                    fdir, fname = os.path.split(user.image.path)
                    zip_path = os.path.join('users', fname)

                    zf.write(user.image.path, zip_path)

        serializer_b = CompleteBulletinSerializer(bulletins, many = True)
        serializer_w = CompleteWebpageSerializer(webpages, many = True)
        serializer_y = CompleteYTVideoSerializer(ytvideos, many = True)
        serializer_f = CompleteFileLinkSerializer(filelinks, many = True)
        serializer_l = CompleteLinkSerializer(links, many = True)
        serializer_p = CompletePDFFileSerializer(pdffiles, many = True)
        serializer_g = CompleteGoalSerializer(goals, many = True)
        serializer_c = CompleteWebconferenceSerializer(webconferences, many = True)
    else:
        serializer_b = SimpleBulletinSerializer(bulletins, many = True)
        serializer_w = SimpleWebpageSerializer(webpages, many = True)
        serializer_y = SimpleYTVideoSerializer(ytvideos, many = True)
        serializer_f = SimpleFileLinkSerializer(filelinks, many = True)
        serializer_l = SimpleLinkSerializer(links, many = True)
        serializer_p = SimplePDFFileSerializer(pdffiles, many = True)
        serializer_g = SimpleGoalSerializer(goals, many = True)
        serializer_c = SimpleWebconferenceSerializer(webconferences, many = True)

    if len(serializer_b.data) > 0:
        data_list.append(serializer_b.data)

    if len(serializer_w.data) > 0:
        data_list.append(serializer_w.data)
    
    if len(serializer_y.data) > 0:
        data_list.append(serializer_y.data)

    if len(serializer_f.data) > 0:
        data_list.append(serializer_f.data)

    if len(serializer_l.data) > 0:
        data_list.append(serializer_l.data)

    if len(serializer_p.data) > 0:
        data_list.append(serializer_p.data)

    if len(serializer_g.data) > 0:
        data_list.append(serializer_g.data)

    if len(serializer_c.data) > 0:
        data_list.append(serializer_c.data)

    json.dump(data_list, file)

    file.close()

    fdir, fname = os.path.split("backup.json")
    zip_path = os.path.join("", fname)

    # Add file, at correct path
    zf.write("backup.json", zip_path)

    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    resp['Content-Length'] = s.tell()

    return resp

class Restore(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'subjects/restore.html'
    model = Subject

    def dispatch(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug = kwargs.get('slug', ''))

        if not has_subject_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(Restore, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Restore, self).get_context_data(**kwargs)

        subject = get_object_or_404(Subject, slug = self.kwargs.get('slug', ''))
        
        context['title'] = _('%s - Restore')%(str(subject))
        context['subject'] = subject

        return context

@login_required
def realize_restore(request, subject):
    subjetc = get_object_or_404(Subject, slug = subject)
    zip_file = request.FILES.get('zip_file', None)

    if zip_file:
        if zipfile.is_zipfile(zip_file):
            file = zipfile.ZipFile(zip_file)
            total_files = len(file.namelist())

            json_file = file.namelist()[total_files-1]

            dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")
            
            path = file.extract(json_file, dst_path)

            with open(path) as bkp_file:
                data = json.loads(bkp_file.read())

                for line in data:
                    if len(line) > 0:
                        if "_my_subclass" in line[0]:
                            if line[0]["_my_subclass"] == "webpage":
                                if "students" in line[0]:
                                    serial = CompleteWebpageSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                                else:
                                    serial = SimpleWebpageSerializer(data = line, many = True, context = {'subject': subject})
                            elif line[0]["_my_subclass"] == "bulletin":
                                if "students" in line[0]:
                                    print(file.namelist())
                                    print(line[0]["file_content"])
                                    print(line[0]["file_content"] in file.namelist())
                                    serial = CompleteBulletinSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                                else:
                                    serial = SimpleBulletinSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                            elif line[0]["_my_subclass"] == "filelink":
                                if "students" in line[0]:
                                    serial = CompleteFileLinkSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                                else:
                                    serial = SimpleFileLinkSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                            elif line[0]["_my_subclass"] == "link":
                                if "students" in line[0]:
                                    serial = CompleteLinkSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                                else:
                                    serial = SimpleLinkSerializer(data = line, many = True, context = {'subject': subject})
                            elif line[0]["_my_subclass"] == "pdffile":
                                if "students" in line[0]:
                                    serial = CompletePDFFileSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                                else:
                                    serial = SimplePDFFileSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                            elif line[0]["_my_subclass"] == "goals":
                                if "students" in line[0]:
                                    serial = CompleteGoalSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                                else:
                                    serial = SimpleGoalSerializer(data = line, many = True, context = {'subject': subject})
                            elif line[0]["_my_subclass"] == "ytvideo":
                                if "students" in line[0]:
                                    serial = CompleteYTVideoSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                                else:
                                    serial = SimpleYTVideoSerializer(data = line, many = True, context = {'subject': subject})
                            elif line[0]["_my_subclass"] == "webconference":
                                if "students" in line[0]:
                                    serial = CompleteWebconferenceSerializer(data = line, many = True, context = {'subject': subject, 'files': file})
                                else:
                                    serial = SimpleWebconferenceSerializer(data = line, many = True, context = {'subject': subject})
                            
                            serial.is_valid()
                            serial.save()

    messages.success(request, _('Backup restored successfully!'))

    return redirect(reverse_lazy('subjects:restore', kwargs = {"slug": subject}))