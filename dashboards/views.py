""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import render

from django.views import generic
from django.db.models import Count
from django.core.urlresolvers import reverse_lazy, reverse

from subjects.models import Tag, Subject
from topics.models import Resource
from users.models import User
from django.http import HttpResponse, JsonResponse
from log.models import Log
import operator
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpResponseForbidden

from datetime import date, timedelta, datetime
import calendar
from collections import OrderedDict

from categories.models import Category

from subjects.models import Subject, Tag

from .utils import get_pend_graph, getAccessedTags, getTagAccessess, getOtherIndicators


from log.mixins import LogMixin
from log.decorators import log_decorator_ajax
from log.models import Log

from amadeus.permissions import has_category_permissions, has_subject_permissions, has_subject_view_permissions, has_resource_permissions


import json

class GeneralView(LogMixin, generic.TemplateView):
    template_name = "dashboards/general.html"

    log_component = "General_Dashboard"
    log_action = "view"
    log_resource = "General_Dashboard"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
       
        if not request.user.is_staff:
            return redirect('dashboards:view_categories')
        return super(GeneralView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = {}
        
        self.createLog(actor = self.request.user)
        context['months'] = self.get_last_twelve_months()
        context['child_template'] = "dashboards/general_body.html"
        context['javascript_files'] = ["analytics/js/d3.v5.min.js",
                                        "analytics/js/d3.v3.min.js",
                                        "analytics/js/JSUtil.js",
                                        "analytics/js/ToolTip.js",
                                        "analytics/js/HeatMap.js",
                                        "analytics/js/d3-collection.v1.min.js",
                                        "analytics/js/d3-dispatch.v1.min.js",
                                        "analytics/js/d3-force.v1.min.js",
                                        "analytics/js/d3-timer.v1.min.js",
                                        "analytics/js/BubbleChart.js",
                                        "analytics/js/cloud.min.js",
                                        "analytics/js/charts.js",
                                        "dashboards/js/behavior.js"]
        context['style_files'] = ['dashboards/css/general.css']
        return context

    def get_last_twelve_months(self):
        today = date.today()
        months = []
        month_mappings = { 1: _('January'), 2: _('February'), 3: _('March'), 4: _('April'), 5: _('May'), 6: _('June'), 7: _('July')
            , 8: _('August'), 9: _('September'), 10: _('October'), 11: _('November'), 12:  _('December')}
        date_used = today #the date used for solving the inital month problem
        offset = 0 #offset is the amount of weeks I had to shift so I could change the month if 4 weeks weren't enough
        for i in range(12):

            operation_date = today - timedelta(weeks= (4*i + offset))
            while date_used.month == operation_date.month:
                offset += 2
                operation_date = today - timedelta(weeks= (4*i + offset))

            months.append(month_mappings[date_used.month] + '/' + str(date_used.year))
            date_used = operation_date
        return months
    

class CategoryView(LogMixin, generic.TemplateView):
    template_name = "dashboards/category.html"
    
    log_component = "Category_Dashboard"
    log_action = "view"
    log_resource = "Category_Dashboard"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        if  Category.objects.filter(coordinators__id = self.request.user.id).exists() or self.request.user.is_staff:
            return super(CategoryView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('users:login')


    def get_context_data(self, **kwargs):
        context = {}
        self.createLog(actor = self.request.user)
        
        context['months'] = self.get_last_twelve_months()

        context['categories'] = self.categories_associated_with_user(self.request.user)
        context['javascript_files'] = ["analytics/js/d3.v5.min.js",
                                        "analytics/js/d3.v3.min.js",
                                        "analytics/js/JSUtil.js",
                                        "analytics/js/ToolTip.js",
                                        "analytics/js/cloud.min.js",
                                        "analytics/js/charts.js", 
                                        "dashboards/js/behavior_categories.js",
                                        "dashboards/js/charts_category.js"]
        context['style_files'] = ['dashboards/css/general.css', 'dashboards/css/dashboards_category.css']
        return context

    
    def get_last_twelve_months(self):
        today = date.today()
        months = []
        month_mappings = { 1: _('January'), 2: _('February'), 3: _('March'), 4: _('April'), 5: _('May'), 6: _('June'), 7: _('July')
            , 8: _('August'), 9: _('September'), 10: _('October'), 11: _('November'), 12:  _('December')}
        date_used = today #the date used for solving the inital month problem
        offset = 0 #offset is the amount of weeks I had to shift so I could change the month if 4 weeks weren't enough
        for i in range(12):

            operation_date = today - timedelta(weeks= (4*i + offset))
            while date_used.month == operation_date.month:
                offset += 2
                operation_date = today - timedelta(weeks= (4*i + offset))

            months.append(month_mappings[date_used.month] + '/' + str(date_used.year))
            date_used = operation_date
        return months

    def categories_associated_with_user(self, user):
        if user.is_staff:
            categories = Category.objects.all()
        else:
            categories = Category.objects.filter(coordinators__in = [user])
        return categories

class LogView(LogMixin, generic.TemplateView):
    template_name = "dashboards/general.html"

    log_component = "admin_log"
    log_action = "view"
    log_resource = "admin_log"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        return super(LogView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}
        self.createLog(actor = self.request.user)
        
        context['javascript_files'] = ['dashboards/js/logbehavior.js',
        'dashboards/js/dataTables.bootstrap.min.js', 'dashboards/js/jquery.dataTables.min.js']
        context['child_template'] = "dashboards/log.html"
        context['style_files'] = [ 'dashboards/css/jquery.dataTables.min.css', 'dashboards/css/general.css', 
        'dashboards/css/dataTables.bootstrap.min.css' ]
        return context

    

def load_log_data(request):
    params = request.GET
    init_date = datetime.strptime(params['init_date'], '%Y-%m-%d')

    end_date = datetime.strptime(params['end_date'], '%Y-%m-%d')

    if params.get('category'):
        print("has category")
    logs = Log.objects.filter(datetime__range = (init_date, end_date) )
    logs = parse_log_queryset_to_JSON(logs)
    return JsonResponse(logs, safe=False)


def parse_log_queryset_to_JSON(logs):
    data = []
    for log in logs:
        datum = {}
        datum['user'] = log.user
        datum['resource'] = log.resource
        datum['datetime'] = log.datetime.strftime("%d/%m/%Y %H:%M")
        datum['action'] = log.action
        datum['context'] = log.context
        datum['component'] = log.component
        data.append(datum)
    return data

class SubjectView(LogMixin, generic.TemplateView):
    template_name = "dashboards/subjects.html"

    log_component = "subject"
    log_action = "view"
    log_resource = "analytics"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug=kwargs.get('slug', ''))

        if not has_subject_view_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SubjectView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug = self.kwargs.get('slug', ''))

        if has_subject_permissions(self.request.user, subject):
            return self.render_to_response(self.get_context_data())
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        subject = get_object_or_404(Subject, slug = self.kwargs.get('slug', ''))

        context = {}
        
        context["title"] = _("Analytics")

        self.log_context['category_id'] = subject.category.id
        self.log_context['category_name'] = subject.category.name
        self.log_context['category_slug'] = subject.category.slug
        self.log_context['subject_id'] = subject.id
        self.log_context['subject_name'] = subject.name
        self.log_context['subject_slug'] = subject.slug
        
        if has_subject_permissions(self.request.user, subject):
            student = self.request.POST.get('selected_student', None)
            students = subject.students.all()
            students = sorted(students,key=lambda student: student.username) # Ordem Alfabética
            context['sub_students'] = students
            context['student'] = self.request.POST.get('selected_student', subject.students.first().email)

            self.log_context['student'] = context['student']

            if not student is None:
                student = User.objects.get(email = student)
                context["graph_data"] = json.dumps(get_pend_graph(student, subject))
                context["tags_cloud"] = reverse('dashboards:cloudy_data', args = (subject.slug, student.email,), kwargs = {})
                context["metrics_url"] = reverse('dashboards:other_metrics', args = (subject.slug, student.email,), kwargs = {})
            else:
                student = User.objects.get(email = context['student'])
                context["graph_data"] = json.dumps(get_pend_graph(student, subject))
                context["tags_cloud"] = reverse('dashboards:cloudy_data', args = (subject.slug, student.email,), kwargs = {})
                context["metrics_url"] = reverse('dashboards:other_metrics', args = (subject.slug, student.email,), kwargs = {})
        else:
            context["tags_cloud"] = reverse('dashboards:cloudy_data', args = (subject.slug, self.request.user.email,), kwargs = {})
            context["graph_data"] = json.dumps(get_pend_graph(self.request.user, subject))
            context["metrics_url"] = reverse('dashboards:other_metrics', args = (subject.slug, self.request.user.email,), kwargs = {})

        context["subject"] = subject
        context["qtd_students"] = subject.students.count()
        context['javascript_files'] = []
        context['style_files'] = ['dashboards/css/style.css','dashboards/css/general.css', 'dashboards/css/dashboards_category.css']
        
        super(SubjectView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 

        return context

def tag_accessess(request, tag, subject, email):
    sub = Subject.objects.get(slug = subject)
    user = User.objects.get(email = email)
    tag = Tag.objects.get(id = tag)

    return JsonResponse(getTagAccessess(sub, tag, user), safe = False)

def other_metrics(request, subject, email):
    sub = Subject.objects.get(slug = subject)
    user = User.objects.get(email = email)

    return JsonResponse(getOtherIndicators(sub, user), safe = False)

def cloudy_data(request, subject, email):
    sub = Subject.objects.get(slug = subject)
    user = User.objects.get(email = email)

    return JsonResponse(getAccessedTags(sub, user), safe = False)
