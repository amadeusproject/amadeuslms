""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count

from dateutil import parser
from datetime import datetime
from django.utils import formats, timezone

from amadeus.permissions import has_subject_view_permissions, has_category_permission, has_subject_permissions

from subjects.models import Subject
from categories.models import Category
from users.models import User

from log.models import Log
from log.mixins import LogMixin
from log.decorators import log_decorator, log_decorator_ajax
import time

from .models import Notification
from .utils import get_order_by, is_date, strToDate

class SubjectNotifications(LoginRequiredMixin, LogMixin, generic.ListView):
    log_component = 'pendencies'
    log_action = 'view'
    log_resource = 'pendencies'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    context_object_name = 'notifications'
    template_name = 'notifications/subject.html'
    paginate_by = 10
    total = 0

    students = None

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        if not has_subject_view_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SubjectNotifications, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        if has_subject_permissions(self.request.user, subject):
            self.students = User.objects.filter(subject_student = subject).order_by('social_name', 'username')

            notifications = Notification.objects.filter(user = self.students.first(), task__resource__topic__subject = subject, creation_date = datetime.now()).order_by("task__limit_date", "task__end_date")
        else:
            notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject, creation_date = datetime.now()).order_by("task__limit_date", "task__end_date")
            notifications.update(viewed = True)
            
        self.total = notifications.count()

        return notifications

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        user = request.POST.get('selected_student', None)

        if has_subject_permissions(request.user, subject):
            self.students = User.objects.filter(subject_student = subject).order_by('social_name', 'username')

            if not user is None:
                self.object_list = Notification.objects.filter(user__email = user, task__resource__topic__subject = subject, creation_date = datetime.now()).order_by("task__limit_date", "task__end_date")
            else:
                self.object_list = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject, creation_date = datetime.now()).order_by("task__limit_date", "task__end_date")
        else:
            self.object_list = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject, creation_date = datetime.now()).order_by("task__limit_date", "task__end_date")

        self.total = self.object_list.count()

        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(SubjectNotifications, self).get_context_data(**kwargs)

        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        context['title'] = _('%s - Pendencies')%(subject.name)
        context['subject'] = subject
        context['total'] = self.total

        if not self.students is None:
            context['sub_students'] = self.students
            context['student'] = self.request.POST.get('selected_student', self.students.first().email)
        else:
            context['student'] = None

        update_pendencies = Log.objects.filter(action = "cron", component = "notifications").order_by('-datetime')

        if update_pendencies.count() > 0:
            last_update = update_pendencies[0]

            context['last_update'] = last_update.datetime

        self.log_context['subject_id'] = subject.id
        self.log_context['subject_name'] = subject.name
        self.log_context['subject_slug'] = subject.slug
        self.log_context['view_page'] = self.request.GET.get("page", 1)
        self.log_context['timestamp_start'] = str(int(time.time()))

        super(SubjectNotifications, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        self.request.session['log_id'] = Log.objects.latest('id').id

        return context

class SubjectHistory(LoginRequiredMixin, LogMixin, generic.ListView):
    log_component = 'pendencies'
    log_action = 'view_history'
    log_resource = 'pendencies'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    context_object_name = 'notifications'
    template_name = 'notifications/subject.html'
    paginate_by = 10
    total = 0
    num_rows = 0

    students = None

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        if not has_subject_view_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SubjectHistory, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        order = get_order_by(self.request.GET.get("order_by", None))
        search = self.request.GET.get("search", None)

        if has_subject_permissions(self.request.user, subject):
            user = self.request.GET.get("selected_student", None)

            self.students = User.objects.filter(subject_student = subject).order_by('social_name', 'username')

            if not user is None:
                notifications = Notification.objects.filter(user__email = user, task__resource__topic__subject = subject).order_by(*order)
            else:
                notifications = Notification.objects.filter(user = self.students.first(), task__resource__topic__subject = subject).order_by(*order)
        else:
            notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject).order_by(*order)

        self.total = notifications.filter(creation_date = datetime.now()).count()
        
        if search:
            queries = Q(task__resource__name__icontains = search)
            queries |= Q(task__action__icontains = search)

            if search.isdigit():
                queries |= Q(level = search)

            if is_date(search):
                search_date = strToDate(search)

                queries |= Q(creation_date = search_date)
                queries |= Q(task__limit_date = search_date)
                queries |= Q(task__end_date = search_date)
                queries |= Q(meta__date = search_date)

            notifications = notifications.filter(queries).order_by(*order)

        self.num_rows = notifications.count()

        return notifications

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        order = get_order_by(self.request.POST.get("order_by", None))

        user = request.POST.get('selected_student', None)

        if has_subject_permissions(request.user, subject):
            self.students = User.objects.filter(subject_student = subject).order_by('social_name', 'username')

            if not user is None:
                self.object_list = Notification.objects.filter(user__email = user, task__resource__topic__subject = subject).order_by(*order)
            else:
                self.object_list = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject).order_by(*order)
        else:
            self.object_list = Notification.objects.filter(user = self.request.user, task__resource__topic__subject = subject).order_by(*order)

        self.total = self.object_list.filter(creation_date = datetime.now()).count()

        self.num_rows = self.object_list.count()

        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(SubjectHistory, self).get_context_data(**kwargs)

        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        context['title'] = _('%s - Pendencies')%(subject.name)
        context['subject'] = subject
        context['history'] = True
        context['total'] = self.total
        context['rows'] = self.num_rows
        context['searched'] = self.request.GET.get("search", "")

        if not self.students is None:
            context['sub_students'] = self.students
            context['student'] = self.request.POST.get('selected_student', self.request.GET.get('selected_student', self.students.first().email))
        else:
            context['student'] = None

        self.log_context['subject_id'] = subject.id
        self.log_context['subject_name'] = subject.name
        self.log_context['subject_slug'] = subject.slug
        self.log_context['history_page'] = self.request.GET.get("page", 1)
        self.log_context['searched'] = self.request.GET.get("search", "")
        self.log_context['timestamp_start'] = str(int(time.time()))

        super(SubjectHistory, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        self.request.session['log_id'] = Log.objects.latest('id').id

        return context

class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    context_object_name = 'notifications'
    template_name = 'notifications/index.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        cat = self.kwargs.get('slug', None)

        if cat:
            if not has_category_permission(request.user, cat):
                return redirect(reverse_lazy('subjects:home'))

        return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        cat = self.kwargs.get('slug', None)

        if cat:
            notifications = Notification.objects.filter(user = self.request.user, creation_date = datetime.now(), task__resource__topic__subject__category__slug = cat).values('task__resource__topic__subject', 'task__resource__topic__subject__name').annotate(total = Count('task__resource__topic__subject'))
        else:
            notifications = Notification.objects.filter(user = self.request.user, creation_date = datetime.now()).values('task__resource__topic__subject', 'task__resource__topic__subject__name').annotate(total = Count('task__resource__topic__subject'))

        return notifications

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['title'] = _('Pendencies')

        update_pendencies = Log.objects.filter(action = "cron", component = "notifications").order_by('-datetime')

        if update_pendencies.count() > 0:
            last_update = update_pendencies[0]

            context['last_update'] = last_update.datetime

        cat = self.kwargs.get('slug', None)

        if cat:
            context['category'] = get_object_or_404(Category, slug = cat)
        else:
            context['pendencies_menu_active'] = "subjects_menu_active"


        return context

class AjaxNotifications(LoginRequiredMixin, generic.ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    context_object_name = 'notifications'
    template_name = 'notifications/_view.html'

    def get_queryset(self):
        subject_id = self.kwargs.get('id', '')
        
        notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject__id = subject_id, creation_date = datetime.now()).order_by("task__limit_date", "task__end_date")

        notifications.update(viewed = True)

        return notifications

    def get_context_data(self, **kwargs):
        context = super(AjaxNotifications, self).get_context_data(**kwargs)

        subject_id = self.kwargs.get('id', '')
        subject = Subject.objects.get(id = subject_id)

        context['subject_id'] = subject_id
        context['subject'] = subject
        
        return context

class AjaxHistory(LoginRequiredMixin, generic.ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    context_object_name = 'notifications'
    template_name = 'notifications/_ajax_history.html'

    def get_queryset(self):
        subject_id = self.kwargs.get('id', '')

        order = get_order_by(self.request.GET.get("order_by", None))
        search = self.request.GET.get("search", None)

        notifications = Notification.objects.filter(user = self.request.user, task__resource__topic__subject__id = subject_id).order_by(*order)

        if search:
            queries = Q(task__resource__name__icontains = search)
            queries |= Q(task__action__icontains = search)

            if search.isdigit():
                queries |= Q(level = search)

            if is_date(search):
                search_date = strToDate(search)

                queries |= Q(creation_date = search_date)
                queries |= Q(task__limit_date = search_date)
                queries |= Q(task__end_date = search_date)
                queries |= Q(meta__date = search_date)

            notifications = notifications.filter(queries).order_by(*order)

        self.num_rows = notifications.count()

        return notifications

    def get_context_data(self, **kwargs):
        context = super(AjaxHistory, self).get_context_data(**kwargs)

        subject_id = self.kwargs.get('id', '')
        subject = Subject.objects.get(id = subject_id)

        context['subject_id'] = subject_id
        context['subject'] = subject
        context['rows'] = self.num_rows
        context['searched'] = self.request.GET.get("search", "")
        context['order_by'] = self.request.GET.get("order_by", "")

        return context

@login_required
@log_decorator('pendencies', 'set_goal', 'pendencies')
def set_goal(request):
    if request.method == "POST" and request.is_ajax():
        meta = request.POST.get('meta', None)

        if not meta:
            return JsonResponse({'error': True, 'message': _('No goal date received')})

        meta = parser.parse(meta)

        notify_id = request.POST.get('id', None)

        if not notify_id:
            return JsonResponse({'error': True, 'message': _('Could not identify the notification')})

        notification = get_object_or_404(Notification, id = notify_id)

        meta = timezone.make_aware(meta, timezone.get_current_timezone())

        if meta < timezone.now():
            return JsonResponse({'error': True, 'message': _("The goal date should be equal or after today's date")})

        if meta.date() > notification.task.resource.topic.subject.end_date:
            return JsonResponse({'error': True, 'message': _("The goal date should be equal or before subject's date")})

        notification.meta = meta
        notification.save()

        log_context = {}
        log_context['notification_id'] = notification.id
        log_context['notification'] = str(notification)

        request.log_context = log_context

        if notification.level == 2:
            message = _('Your new goal to realize the task %s is %s')%(str(notification), formats.date_format(meta, "SHORT_DATETIME_FORMAT"))
        else:
            message = _('Your goal to realize the task %s is %s')%(str(notification), formats.date_format(meta, "SHORT_DATETIME_FORMAT"))

    return JsonResponse({'error': False, 'message': message})

@log_decorator_ajax('pendencies', 'view', 'pendencies')
def pendencies_view_log(request, subject):
    action = request.GET.get('action')

    if action == 'open':
        subject = get_object_or_404(Subject, id = subject)

        log_context = {}
        log_context['subject_id'] = subject.id
        log_context['subject_name'] = subject.name
        log_context['subject_slug'] = subject.slug
        log_context['timestamp_start'] = str(int(time.time()))
        log_context['timestamp_end'] = '-1'

        request.log_context = log_context

        log_id = Log.objects.latest('id').id

        return JsonResponse({'message': 'ok', 'log_id': log_id})

    return JsonResponse({'message': 'ok'})

@log_decorator_ajax('pendencies', 'view_history', 'pendencies')
def pendencies_hist_log(request, subject):
    action = request.GET.get('action')

    if action == 'open':
        subject = get_object_or_404(Subject, id = subject)

        log_context = {}
        log_context['subject_id'] = subject.id
        log_context['subject_name'] = subject.name
        log_context['subject_slug'] = subject.slug
        log_context['timestamp_start'] = str(int(time.time()))
        log_context['timestamp_end'] = '-1'

        request.log_context = log_context

        log_id = Log.objects.latest('id').id

        return JsonResponse({'message': 'ok', 'log_id': log_id})

    return JsonResponse({'message': 'ok'})