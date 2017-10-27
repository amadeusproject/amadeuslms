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
from django.core.urlresolvers import reverse_lazy

from subjects.models import Tag, Subject
from topics.models import Resource
from users.models import User
from django.http import HttpResponse, JsonResponse
from log.models import Log
import operator
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404, redirect

from datetime import date, timedelta, datetime
import calendar
from collections import OrderedDict

from categories.models import Category


from log.mixins import LogMixin
from log.decorators import log_decorator_ajax
from log.models import Log

from amadeus.permissions import has_category_permissions


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
        context['javascript_files'] = ["analytics/js/charts.js", "dashboards/js/behavior.js"]
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
        context['javascript_files'] = ["analytics/js/charts.js", "dashboards/js/behavior_categories.js",
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