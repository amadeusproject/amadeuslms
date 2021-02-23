""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import render

from django.views import generic
from django.db.models import Count, Q
from django.core.urlresolvers import reverse_lazy, reverse

from subjects.models import Tag, Subject
from topics.models import Resource
from users.models import User
from django.http import HttpResponse, JsonResponse
from log.models import Log
import operator
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import HttpResponseForbidden

from datetime import date, timedelta, datetime
import calendar
from collections import OrderedDict

from categories.models import Category

from subjects.models import Subject, Tag

from .utils import (
    get_pend_graph,
    getAccessedTags,
    getTagAccessess,
    getOtherIndicators,
    studentsAccess,
    parse_date,
    accessResourceCount,
    getAccessedTagsPeriod,
    getTagAccessessPeriod,
    monthly_users_activity,
    my_categories,
    general_monthly_users_activity,
    generalUsersAccess,
    general_logs,
    active_users_qty,
    functiontable,
    xml_users,
)

from log.mixins import LogMixin
from log.decorators import log_decorator_ajax
from log.models import Log

from amadeus.permissions import (
    has_analytics_permissions,
    has_category_permissions,
    has_subject_permissions,
    has_subject_view_permissions,
    has_resource_permissions,
)

import json

from .avatar import (
    generalInfo,
    cloudInfo,
    cloudTips,
    indicatorsInfo,
    indicatorsTips,
    ganntInfo,
    ganntTips,
)

import numpy as np
from plotly.io import templates
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from django.template.loader import get_template

from django.utils.formats import get_format
from datatableview import Datatable, columns
from datatableview.views import DatatableView

import xlwt


class GeneralView(LoginRequiredMixin, LogMixin, generic.TemplateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "dashboards/general.html"

    log_component = "General_Dashboard"
    log_action = "view"
    log_resource = "General_Dashboard"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_staff:
            return redirect("dashboards:view_categories")

        return super(GeneralView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}

        self.createLog(actor=self.request.user)
        context["months"] = self.get_last_twelve_months()
        context["child_template"] = "dashboards/general_body.html"
        context["javascript_files"] = [
            "analytics/js/d3.v5.min.js",
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
            "dashboards/js/behavior.js",
        ]
        context["style_files"] = ["dashboards/css/general.css"]
        return context

    def get_last_twelve_months(self):
        today = date.today()
        months = []
        month_mappings = {
            1: _("January"),
            2: _("February"),
            3: _("March"),
            4: _("April"),
            5: _("May"),
            6: _("June"),
            7: _("July"),
            8: _("August"),
            9: _("September"),
            10: _("October"),
            11: _("November"),
            12: _("December"),
        }
        date_used = today  # the date used for solving the inital month problem
        offset = 0  # offset is the amount of weeks I had to shift so I could change the month if 4 weeks weren't enough
        for i in range(12):

            operation_date = today - timedelta(weeks=(4 * i + offset))
            while date_used.month == operation_date.month:
                offset += 2
                operation_date = today - timedelta(weeks=(4 * i + offset))

            months.append(month_mappings[date_used.month] + "/" + str(date_used.year))
            date_used = operation_date
        return months


class CategoryView(LoginRequiredMixin, LogMixin, generic.TemplateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "dashboards/manager/index_category.html"

    log_component = "Category_Dashboard"
    log_action = "view"
    log_resource = "Category_Dashboard"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        if not has_analytics_permissions(self.request.user):
            return redirect(reverse_lazy("subjects:home"))

        return super(CategoryView, self).dispatch(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = {}
        self.createLog(actor=self.request.user)

        context["title"] = _("Analytics")
        context["dashboard_menu_active"] = "subjects_menu_active"

        context["data_ini"] = timezone.localtime(timezone.now()) - timedelta(days=7)
        context["data_end"] = timezone.localtime(timezone.now())

        context["months"] = self.get_last_twelve_months()
        
        context["categories"] = self.categories_associated_with_user(self.request.user)
        context["selectedCategory"] = context["categories"][0] 

        context["child_template"] = "dashboards/general_body.html"
        context["javascript_files"] = [
            "analytics/js/d3.v5.min.js",
            "analytics/js/d3.v3.min.js",
            "analytics/js/JSUtil.js",
            "analytics/js/ToolTip.js",
            "analytics/js/d3-collection.v1.min.js",
            "analytics/js/d3-dispatch.v1.min.js",
            "analytics/js/d3-force.v1.min.js",
            "analytics/js/d3-timer.v1.min.js",
            "analytics/js/BubbleChart.js",
            "analytics/js/cloud.min.js",
            "analytics/js/charts.js",
            "dashboards/js/behavior.js",
        ]
        context["style_files"] = ["dashboards/css/general.css"]

        return context

    def get_last_twelve_months(self):
        today = date.today()
        months = []
        month_mappings = {
            1: _("January"),
            2: _("February"),
            3: _("March"),
            4: _("April"),
            5: _("May"),
            6: _("June"),
            7: _("July"),
            8: _("August"),
            9: _("September"),
            10: _("October"),
            11: _("November"),
            12: _("December"),
        }
        date_used = today  # the date used for solving the inital month problem
        offset = 0  # offset is the amount of weeks I had to shift so I could change the month if 4 weeks weren't enough
        for i in range(12):

            operation_date = today - timedelta(weeks=(4 * i + offset))
            while date_used.month == operation_date.month:
                offset += 2
                operation_date = today - timedelta(weeks=(4 * i + offset))

            months.append(month_mappings[date_used.month] + "/" + str(date_used.year))
            date_used = operation_date
        return months

    def categories_associated_with_user(self, user):
        if user.is_staff:
            categories = Category.objects.all().order_by("name")
        else:
            categories = Category.objects.filter(coordinators__in=[user]).distinct().order_by("name")
        return categories


class LogView(LoginRequiredMixin, LogMixin, generic.TemplateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "dashboards/general.html"

    log_component = "admin_log"
    log_action = "view"
    log_resource = "admin_log"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        return super(LogView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}
        self.createLog(actor=self.request.user)

        context["javascript_files"] = [
            "dashboards/js/logbehavior.js",
            "dashboards/js/dataTables.bootstrap.min.js",
            "dashboards/js/jquery.dataTables.min.js",
        ]
        context["child_template"] = "dashboards/log.html"
        context["style_files"] = [
            "dashboards/css/jquery.dataTables.min.css",
            "dashboards/css/general.css",
            "dashboards/css/dataTables.bootstrap.min.css",
        ]
        return context


def load_log_data(request):
    params = request.GET
    init_date = datetime.strptime(params["init_date"], "%Y-%m-%d")

    end_date = datetime.strptime(params["end_date"], "%Y-%m-%d")

    if params.get("category"):
        print("has category")
    logs = Log.objects.filter(datetime__range=(init_date, end_date))
    logs = parse_log_queryset_to_JSON(logs)
    return JsonResponse(logs, safe=False)


def parse_log_queryset_to_JSON(logs):
    data = []
    for log in logs:
        datum = {}
        datum["user"] = log.user
        datum["resource"] = log.resource
        datum["datetime"] = log.datetime.strftime("%d/%m/%Y %H:%M")
        datum["action"] = log.action
        datum["context"] = log.context
        datum["component"] = log.component
        data.append(datum)
    return data


class SubjectView(LoginRequiredMixin, LogMixin, generic.TemplateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "dashboards/subjects.html"

    log_component = "subject"
    log_action = "view"
    log_resource = "analytics"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug=kwargs.get("slug", ""))

        if not has_subject_view_permissions(request.user, subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(SubjectView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug=self.kwargs.get("slug", ""))

        if has_subject_permissions(self.request.user, subject):
            return self.render_to_response(self.get_context_data())
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        subject = get_object_or_404(Subject, slug=self.kwargs.get("slug", ""))

        context = {}

        context["title"] = _("Analytics")

        self.log_context["category_id"] = subject.category.id
        self.log_context["category_name"] = subject.category.name
        self.log_context["category_slug"] = subject.category.slug
        self.log_context["subject_id"] = subject.id
        self.log_context["subject_name"] = subject.name
        self.log_context["subject_slug"] = subject.slug

        context["avatar_audios"] = []
        context["avatar_ganntInfo"] = []
        context["avatar_ganntTips"] = []

        if has_subject_permissions(self.request.user, subject):
            student = self.request.POST.get("selected_student", None)

            if student is None:
                student = self.kwargs.get("email", None)

            students = subject.students.all()
            students = sorted(
                students, key=lambda student: student.username
            )  # Ordem Alfabética
            context["sub_students"] = students
            context["student"] = (
                student if not student is None else subject.students.first().email
            )

            self.log_context["student"] = context["student"]

            if not student is None:
                student = User.objects.get(email=student)
                context["graph_data"] = get_pend_graph(student, subject)
                context["tags_cloud"] = reverse(
                    "dashboards:cloudy_data",
                    args=(subject.slug, student.email,),
                    kwargs={},
                )
                context["metrics_url"] = reverse(
                    "dashboards:other_metrics",
                    args=(subject.slug, student.email,),
                    kwargs={},
                )
            else:
                student = User.objects.get(email=context["student"])
                context["graph_data"] = get_pend_graph(student, subject)
                context["tags_cloud"] = reverse(
                    "dashboards:cloudy_data",
                    args=(subject.slug, student.email,),
                    kwargs={},
                )
                context["metrics_url"] = reverse(
                    "dashboards:other_metrics",
                    args=(subject.slug, student.email,),
                    kwargs={},
                )

            if subject.display_avatar:
                context["avatar_audios"] = generalInfo(subject, student)
                context["avatar_ganntInfo"] = ganntInfo()
                context["avatar_ganntTips"] = ganntTips(context["graph_data"])
        else:
            context["tags_cloud"] = reverse(
                "dashboards:cloudy_data",
                args=(subject.slug, self.request.user.email,),
                kwargs={},
            )
            context["graph_data"] = get_pend_graph(self.request.user, subject)
            context["metrics_url"] = reverse(
                "dashboards:other_metrics",
                args=(subject.slug, self.request.user.email,),
                kwargs={},
            )

            if subject.display_avatar:
                context["avatar_audios"] = generalInfo(subject, self.request.user)
                context["avatar_ganntInfo"] = ganntInfo()
                context["avatar_ganntTips"] = ganntTips(context["graph_data"])

        context["graph_data"] = json.dumps(context["graph_data"], default=str)
        context["subject"] = subject
        context["qtd_students"] = subject.students.count()
        context["javascript_files"] = []
        context["style_files"] = [
            "dashboards/css/style.css",
            "dashboards/css/general.css",
            "dashboards/css/dashboards_category.css",
        ]

        super(SubjectView, self).createLog(
            self.request.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        return context


def tag_accessess(request, tag, subject, email):
    sub = Subject.objects.get(slug=subject)
    tag = Tag.objects.get(id=tag)
    user = User.objects.get(email=email)
    return JsonResponse(getTagAccessess(sub, tag, user), safe=False)


def tag_accessess_period(request, tag, subject, email, data_ini, data_end):
    if data_ini == "":
        data_ini = request.GET.get("data_ini", "")
    if data_end == "":
        data_end = request.GET.get("data_end", "")
    sub = Subject.objects.get(slug=subject)
    tag = Tag.objects.get(id=tag)
    user = User.objects.get(email=email)
    return JsonResponse(
        getTagAccessessPeriod(sub, tag, user, data_ini, data_end), safe=False
    )


def other_metrics(request, subject, email):
    sub = Subject.objects.get(slug=subject)
    user = User.objects.get(email=email)

    indicatorsData = getOtherIndicators(sub, user)
    infoAudios = [] #indicatorsInfo()
    tipAudios = [] #indicatorsTips(sub, indicatorsData)

    return JsonResponse(
        {"indicators": indicatorsData, "info": infoAudios, "tips": tipAudios},
        safe=False,
    )


def cloudy_data(request, subject, email=None):
    sub = Subject.objects.get(slug=subject)
    user = User.objects.get(email=email)

    cloudData = getAccessedTags(sub, user)
    infoAudios = [] #cloudInfo(cloudData)
    tipAudios = [] #cloudTips(cloudData)

    return JsonResponse(
        {"cloud": cloudData, "info": infoAudios, "tips": tipAudios}, safe=False
    )


def cloudy_data_period(request, subject, email=None):
    data_end = request.GET.get("data_end", "")
    data_ini = request.GET.get("data_ini", "")

    if not data_ini == "":
        data_ini = parse_date(data_ini)

    if not data_end == "":
        data_end = parse_date(data_end)
    sub = Subject.objects.get(slug=subject)
    if email == None:
        user = request.user
    else:
        user = User.objects.get(email=email)
    return JsonResponse(
        getAccessedTagsPeriod(sub, user, data_ini, data_end), safe=False
    )


###### Subjects Teacher Dashboard #######
class SubjectTeacher(LoginRequiredMixin, LogMixin, generic.TemplateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "dashboards/teacher/index.html"

    log_component = "subject"
    log_action = "view"
    log_resource = "analytics"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug=kwargs.get("slug", ""))

        if not has_subject_permissions(request.user, subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(SubjectTeacher, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, slug=self.kwargs.get("slug", ""))

        if has_subject_permissions(self.request.user, subject):
            return self.render_to_response(self.get_context_data())
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        subject = get_object_or_404(Subject, slug=self.kwargs.get("slug", ""))
        context = {}

        context["title"] = _("Analytics")

        context["subject"] = subject
        context["data_ini"] = datetime.now() - timedelta(days=30)
        context["data_end"] = datetime.now()

        self.log_context["category_id"] = subject.category.id
        self.log_context["category_name"] = subject.category.name
        self.log_context["category_slug"] = subject.category.slug
        self.log_context["subject_id"] = subject.id
        self.log_context["subject_name"] = subject.name
        self.log_context["subject_slug"] = subject.slug

        super(SubjectTeacher, self).createLog(
            self.request.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        return context


#### General Manager Dashboard  -  Begin  ####
class GeneralManager(LoginRequiredMixin, LogMixin, generic.TemplateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "dashboards/manager/index.html"

    log_component = "Manager Dashboard"
    log_action = "view"
    log_resource = "Manager Dashboard"
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse_lazy("subjects:home"))

        return super(GeneralManager, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}
        # categorias=my_categories(self.request.user)
        context["title"] = _("Analytics")
        context["dashboard_menu_active"] = "subjects_menu_active"

        # context["data_ini"] = datetime.now() - timedelta(days=30)
        context["data_ini"] = timezone.localtime(timezone.now()) - timedelta(days=7)
        context["data_end"] = timezone.localtime(timezone.now())
        # context["categories"] = categorias
        # context["subjects"] = subjects_by_categories(categorias)

        self.createLog(actor=self.request.user)
        context["months"] = self.get_last_twelve_months()
        context["child_template"] = "dashboards/general_body.html"
        context["javascript_files"] = [
            "analytics/js/d3.v5.min.js",
            "analytics/js/d3.v3.min.js",
            "analytics/js/JSUtil.js",
            "analytics/js/ToolTip.js",
            "analytics/js/d3-collection.v1.min.js",
            "analytics/js/d3-dispatch.v1.min.js",
            "analytics/js/d3-force.v1.min.js",
            "analytics/js/d3-timer.v1.min.js",
            "analytics/js/BubbleChart.js",
            "analytics/js/cloud.min.js",
            "analytics/js/charts.js",
            "dashboards/js/behavior.js",
        ]
        context["style_files"] = ["dashboards/css/general.css"]
        return context

    def get_last_twelve_months(self):
        today = date.today()
        months = []
        month_mappings = {
            1: _("January"),
            2: _("February"),
            3: _("March"),
            4: _("April"),
            5: _("May"),
            6: _("June"),
            7: _("July"),
            8: _("August"),
            9: _("September"),
            10: _("October"),
            11: _("November"),
            12: _("December"),
        }
        date_used = today  # the date used for solving the inital month problem
        offset = 0  # offset is the amount of weeks I had to shift so I could change the month if 4 weeks weren't enough
        for i in range(12):

            operation_date = today - timedelta(weeks=(4 * i + offset))
            while date_used.month == operation_date.month:
                offset += 2
                operation_date = today - timedelta(weeks=(4 * i + offset))

            months.append(month_mappings[date_used.month] + "/" + str(date_used.year))
            date_used = operation_date
        return months


####    General Manager Dashboard  -  End  ####


def resources_accesses_general(request, slug):
    subject = get_object_or_404(Subject, slug=slug)

    data_end = request.GET.get("data_end", "")
    data_ini = request.GET.get("data_ini", "")

    if not data_ini == "":
        data_ini = parse_date(data_ini)

    if not data_end == "":
        data_end = parse_date(data_end)

    data = accessResourceCount(subject, data_ini, data_end)
    return JsonResponse(data, safe=False)


def most_active_users(request, slug):
    subject = get_object_or_404(Subject, slug=slug)

    data_ini = request.GET.get("data_ini", "")
    data_end = request.GET.get("data_end", "")

    if not data_ini == "":
        data_ini = parse_date(data_ini)

    if not data_end == "":
        data_end = parse_date(data_end)

    data = studentsAccess(subject, data_ini, data_end)

    return JsonResponse(data, safe=False)


def heatmap_graph(request, slug):
    subject = get_object_or_404(Subject, slug=slug)

    data_ini = request.GET.get("data_ini", "")
    data_end = request.GET.get("data_end", "")

    if not data_ini == "":
        data_ini = parse_date(data_ini)
    else:
        data_ini = date.today() - timedelta(days=30)

    if not data_end == "":
        data_end = parse_date(data_end)
    else:
        data_end = date.today()

    data = monthly_users_activity(subject, data_ini, data_end)

    return JsonResponse(data, safe=False)


def general_heatmap_graph(request):
    data_ini = request.GET.get("data_ini", "")
    data_end = request.GET.get("data_end", "")
    categoryId = int(request.GET.get("category", 0))

    if not data_ini == "":
        data_ini = parse_date(data_ini)
    else:
        data_ini = date.today() - timedelta(days=7)

    if not data_end == "":
        data_end = parse_date(data_end)
    else:
        data_end = date.today()

    data = general_monthly_users_activity(data_ini, data_end, categoryId)

    return JsonResponse(data, safe=False)


def most_active_users_general(request):
    data_ini = request.GET.get("data_ini", "")
    data_end = request.GET.get("data_end", "")
    categoryId = int(request.GET.get("category", 0))

    if not data_ini == "":
        data_ini = parse_date(data_ini)
    else:
        data_ini = date.today() - timedelta(days=7)

    if not data_end == "":
        data_end = parse_date(data_end)
    else:
        data_end = date.today()

    data = generalUsersAccess(data_ini, data_end, categoryId)

    return JsonResponse(data, safe=False)


def general_logs_chart(request):

    data_ini = request.GET.get("data_ini", "")
    data_end = request.GET.get("data_end", "")
    categoryId = int(request.GET.get("category", 0))

    if not data_ini == "":
        data_ini = parse_date(data_ini)
    else:
        data_ini = date.today() - timedelta(days=7)

    if not data_end == "":
        data_end = parse_date(data_end)
    else:
        data_end = date.today()

    data, minimun, maximun, total = general_logs(request.user, data_ini, data_end, categoryId)

    return JsonResponse(
        {"data": data, "min": minimun, "max": maximun, "total": total,}, safe=False,
    )


def get_general_active_users(request):
    data_ini = request.GET.get("data_ini", "")
    data_end = request.GET.get("data_end", "")
    categoryId = int(request.GET.get("category", 0))

    if not data_ini == "":
        data_ini = parse_date(data_ini)
    else:
        data_ini = date.today() - timedelta(days=7)

    if not data_end == "":
        data_end = parse_date(data_end)
    else:
        data_end = date.today()

    data = active_users_qty(request.user, data_ini, data_end, categoryId)

    return JsonResponse(data, safe=False)


def get_general_accordion_data(request,):
    data_ini = request.GET.get("data_ini", "")
    data_end = request.GET.get("data_end", "")
    categoryId = int(request.GET.get("category", 0))

    if not data_ini == "":
        data_ini = parse_date(data_ini)
    else:
        data_ini = date.today() - timedelta(days=7)

    if not data_end == "":
        data_end = parse_date(data_end)
    else:
        data_end = date.today()

    data = functiontable(data_ini, data_end, categoryId)

    return JsonResponse(data, safe=False)


def get_xls_users_data(request):
    data_ini = request.POST.get("from", "")
    data_end = request.POST.get("until", "")
    categoryId = int(request.POST.get("selected_category", 0))

    if not data_ini == "":
        data_ini = parse_date(data_ini)
    else:
        data_ini = date.today() - timedelta(days=7)
        # data_ini = date.today() - timedelta(days=7)
    if not data_end == "":
        data_end = parse_date(data_end)
    else:
        data_end = date.today()

    response = xml_users(request.user, data_ini, data_end, categoryId)

    return response

class UserColumn(columns.TextColumn):
    def search(self, model, term):
        return Q(user__icontains=term)

class ActionColumn(columns.TextColumn):
    def search(self, model, term):
        actions = [
            ["access", _("Access")],
            ["view", _("View")],
            ["send", _("Send")],
            ["create", _("Create")],
            ["update", _("Update")],
            ["start", _("Start")],
            ["finish", _("Finish")],
            ["answer", _("Answer")],
            ["delete", _("Delete")],
            ["create_post", _("Create Post")],
            ["create_comment", _("Create Comment")],
            ["edit_post", _("Edit Post")],
            ["edit_comment", _("Edit Comment")],
            ["set_goal", _("Set Goal")],
            ["participate", _("Participate")],
            ["remoe_account", _("Remove Account")],
            ["watch", _("Watch")],
            ["logout", _("Logout")],
            ["view_statistics", _("View Statistics")],
            ["view_new", _("View New")],
            ["view_list_of_news", _("View List of News")],
            ["view_history", _("View History")],
            ["delete_post", _("Delete Post")],
            ["delete_comment", _("Delete Comment")],
            ["search", _("Search")],
            ["change_password", _("Change Password")],
            ["submit", _("Submit")],
            ["click", _("Click")],
            ["initwebconference", _("Init Webconference")],
            ["participating", _("Participating")],
            ["replicate", _("Replicate")]
        ]

        results = (
            [
                y[0] for y in actions
                if term.lower() in y[1].lower()
            ]
        )

        return Q(action__in=results)

class AreaColumn(columns.TextColumn):
    def search(self, model, term):
        elements = [
            ["general_participants", _("General Participants")],
            ["subject_participants", _("Subejct Participants")],
            ["subject/resources", _("Subject/Resources")],
            ["mural", _("Mural")],
            ["post_comments", _("Post Comments")],
            ["filelink", _("File link")],
            ["pdffile", _("PDF File")],
            ["webconference", _("Webconference")],
            ["profile", _("Profile")],
            ["user", _("Users")],
            ["students_group", _("Students Group")],
            ["pendencies", _("Pendencies")],
            ["my_goals", _("My Goals")],
            ["category", _("Category")],
            ["subject", _("Subject")],
            ["goals", _("Goals")],
            ["news", _("News")],
            ["system", _("System")],
            ["ytvideo", _("Youtube Video")],
            ["questionary", _("Questionary")],
            ["Category_Dashboard", _("Category Analytics")],
            ["Manager Dashboard", _("General Analytics")],
            ["topic", _("Topic")],
            ["questions_database", _("Questions Database")],
            ["talk", _("Talk")],
            ["chat", _("Chat")],
            ["webpage", _("Webpage")],
            ["links", _("Links")],
            ["link", _("Links")],
            ["analytics", _("Analytics")]
        ]

        results = (
            [
                y[0] for y in elements
                if term.lower() in y[1].lower()
            ]
        )

        return Q(resource__in=results)

class ContextSubjectColumn(columns.TextColumn):
    def search(self, model, term):
        return Q(context__subject_name=term)

class ContextResourceColumn(columns.TextColumn):
    def search(self, model, term):
        names_resources = [
            "pdffile_name",
            "bulletin_name",
            "ytvideo_name",
            "filelink_name",
            "link_name",
            "goals_name",
            "webpage_name",
            "questionary_name",
            "webconference_name",
            "my_goals_name",
        ]

        conds = Q()

        for resource_name in names_resources:
            conds |= Q(context__contains={resource_name: term})

        return conds

class LogDatatableView(LoginRequiredMixin, DatatableView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "dashboards/manager/log_datatable.html"

    model = Log

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse_lazy("subjects:home"))

        return super(LogDatatableView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        data_ini = self.request.GET.get('data_ini', '')
        data_end = self.request.GET.get('data_end', '')

        if not data_ini == "":
            data_ini = parse_date(data_ini)
        else:
            data_ini = (timezone.localtime(timezone.now()) - timedelta(days=7)).date()

        if not data_end == "":
            data_end = parse_date(data_end)
        else:
            data_end = timezone.localtime(timezone.now()).date()

        logs = Log.objects.filter(datetime__date__gte=data_ini, datetime__date__lte=data_end)

        return logs

    def get_context_data(self, **kwargs):
        context = super(LogDatatableView, self).get_context_data(**kwargs)

        context["title"] = _("Analytics")
        context["dashboard_menu_active"] = "subjects_menu_active"

        data_ini = self.request.GET.get('data_ini', '')
        data_end = self.request.GET.get('data_end', '')

        if not data_ini == "":
            data_ini = parse_date(data_ini)
        else:
            data_ini = timezone.localtime(timezone.now()) - timedelta(days=7)
        if not data_end == "":
            data_end = parse_date(data_end)
        else:
            data_end = timezone.localtime(timezone.now())

        context["data_ini"] = data_ini
        context["data_end"] = data_end

        return context
    
    class datatable_class(Datatable):
        action = ActionColumn(_("Action"), sources=['action'], processor='get_action_name', sortable=False)
        resource = AreaColumn(_("Area"), sources=['resource'], processor='get_area_name', sortable=False)
        user = UserColumn(_("User"), sources=['user'], processor='format_user', sortable=True)
        log_subject = ContextSubjectColumn(_("Subject"), sources=['context'], processor='get_subject_name', sortable=False)
        log_resource = ContextResourceColumn(_("Resource"), sources=['context'], processor='get_resource_name', sortable=False)

        class Meta:
            model = Log
            exclude = ['component', 'id', 'context', 'user_id', 'user_email']
            ordering = ['-datetime']
            labels = {
                'user': _('User'),
                'datetime': _('Date/Time')
            }
            processors = {
                'user': 'format_user',
                'datetime': 'format_datetime'
            }
            structure_template = "datatableview/bootstrap_structure.html"

        def format_user(self, instance, **kwargs):
            url = reverse_lazy("chat:profile", kwargs={'email': instance.user_email})
            fieldValue = "<a href=\"#\" onclick=\"getModalInfo($(this), '0', 'general'); return false;\""
            fieldValue += "data-url='%s'>"%(url)
            fieldValue += instance.user
            fieldValue += "</a>"

            return fieldValue

        def get_action_name(self, instance, **kwargs):
            actions = {
                "access": _("Access"),
                "view": _("View"),
                "send": _("Send"),
                "create": _("Create"),
                "update": _("Update"),
                "start": _("Start"),
                "finish": _("Finish"),
                "answer": _("Answer"),
                "delete": _("Delete"),
                "create_post": _("Create Post"),
                "create_comment": _("Create Comment"),
                "edit_post": _("Edit Post"),
                "edit_comment": _("Edit Comment"),
                "set_goal": _("Set Goal"),
                "participate": _("Participate"),
                "remoe_account": _("Remove Account"),
                "watch": _("Watch"),
                "logout": _("Logout"),
                "view_statistics": _("View Statistics"),
                "view_new": _("View New"),
                "view_list_of_news": _("View List of News"),
                "view_history": _("View History"),
                "delete_post": _("Delete Post"),
                "delete_comment": _("Delete Comment"),
                "search": _("Search"),
                "change_password": _("Change Password"),
                "submit": _("Submit"),
                "click": _("Click"),
                "initwebconference": _("Init Webconference"),
                "participating": _("Participating"),
                "replicate": _("Replicate")
            }

            return actions.get(instance.action, instance.action)

        def get_area_name(self, instance, **kwargs):
            common = ['general', 'category', 'subject', 'message']

            elements = {
                "general_participants": _("General Participants"),
                "subject_participants": _("Subejct Participants"),
                "subject/resources": _("Subject/Resources"),
                "mural": _("Mural"),
                "post_comments": _("Post Comments"),
                "filelink": _("File link"),
                "pdffile": _("PDF File"),
                "webconference": _("Webconference"),
                "profile": _("Profile"),
                "user": _("Users"),
                "students_group": _("Students Group"),
                "pendencies": _("Pendencies"),
                "my_goals": _("My Goals"),
                "category": _("Category"),
                "subject": _("Subject"),
                "goals": _("Goals"),
                "news": _("News"),
                "system": _("System"),
                "ytvideo": _("Youtube Video"),
                "questionary": _("Questionary"),
                "Category_Dashboard": _("Category Analytics"),
                "Manager Dashboard": _("General Analytics"),
                "topic": _("Topic"),
                "questions_database": _("Questions Database"),
                "talk": _("Talk"),
                "chat": _("Chat"),
                "webpage": _("Webpage"),
                "links": _("Links"),
                "link": _("Links"),
                "analytics": _("Analytics")
            }

            if instance.resource in common:
                if instance.component == "mobile":
                    return elements.get("chat", None)

                return elements.get(instance.component, None)

            return elements.get(instance.resource, None)

        def format_datetime(self, instance, **kwargs):
            formatItem = get_format("DATETIME_INPUT_FORMATS")

            return timezone.localtime(instance.datetime).strftime(formatItem[0])

        def get_subject_name(self, instance, **kwargs):
            subject = instance.context.get("subject_name", None)
            subject_slug = instance.context.get("subject_slug", None)

            columnText = ''

            if not subject is None:
                url = reverse_lazy('subjects:view', kwargs={'slug': subject_slug})

                columnText = "<a href='%s' target='blank'>%s</a>"%(url, subject)

            return columnText

        def get_resource_name(self, instance, **kwargs):
            resourceTag = "%s_name"%(instance.resource)
            resourceIdTag = "%s_id"%(instance.resource)

            resource = instance.context.get(resourceTag, None)
            resource_id = instance.context.get(resourceIdTag, None)

            columnText = ''

            resQueryset = Resource.objects.filter(pk=resource_id)

            if not resource is None and instance.component == "resources" and resQueryset.exists():
                resourceObj = resQueryset.get()
            
                columnText = "<a href='%s' target='blank'>%s</a>"%(resourceObj.access_link(), resource)

            return columnText

class CategoryLogDatatableView(LoginRequiredMixin, DatatableView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "dashboards/manager/log_datatable_category.html"

    model = Log

    def dispatch(self, request, *args, **kwargs):
        if not has_analytics_permissions(self.request.user):
            return redirect(reverse_lazy("subjects:home"))

        return super(CategoryLogDatatableView, self).dispatch(request, *args, **kwargs)
        
    def get_queryset(self):
        data_ini = self.request.GET.get('data_ini', '')
        data_end = self.request.GET.get('data_end', '')
        category = self.request.GET.get('category', None)

        if not data_ini == "":
            data_ini = parse_date(data_ini)
        else:
            data_ini = (timezone.localtime(timezone.now()) - timedelta(days=7)).date()

        if not data_end == "":
            data_end = parse_date(data_end)
        else:
            data_end = timezone.localtime(timezone.now()).date()

        if category is None:
            category = self.categories_associated_with_user(self.request.user)[0]
            category = category.id

        logs = Log.objects.filter(datetime__date__gte=data_ini, datetime__date__lte=data_end, context__category_id=category)

        return logs

    def get_context_data(self, **kwargs):
        context = super(CategoryLogDatatableView, self).get_context_data(**kwargs)

        context["title"] = _("Analytics")
        context["dashboard_menu_active"] = "subjects_menu_active"

        data_ini = self.request.GET.get('data_ini', '')
        data_end = self.request.GET.get('data_end', '')

        if not data_ini == "":
            data_ini = parse_date(data_ini)
        else:
            data_ini = timezone.localtime(timezone.now()) - timedelta(days=7)
        if not data_end == "":
            data_end = parse_date(data_end)
        else:
            data_end = timezone.localtime(timezone.now())

        context["data_ini"] = data_ini
        context["data_end"] = data_end

        context["categories"] = self.categories_associated_with_user(self.request.user)
        context["selectedCategory"] = context["categories"][0] 

        return context

    def categories_associated_with_user(self, user):
        if user.is_staff:
            categories = Category.objects.all().order_by("name")
        else:
            categories = Category.objects.filter(coordinators__in=[user]).distinct().order_by("name")
        
        return categories

    class datatable_class(Datatable):
        action = ActionColumn(_("Action"), sources=['action'], processor='get_action_name', sortable=False)
        resource = AreaColumn(_("Area"), sources=['resource'], processor='get_area_name', sortable=False)
        user = UserColumn(_("User"), sources=['user'], processor='format_user', sortable=True)
        log_subject = ContextSubjectColumn(_("Subject"), sources=['context'], processor='get_subject_name', sortable=False)
        log_resource = ContextResourceColumn(_("Resource"), sources=['context'], processor='get_resource_name', sortable=False)

        class Meta:
            model = Log
            exclude = ['component', 'id', 'context', 'user_id', 'user_email']
            ordering = ['-datetime']
            labels = {
                'user': _('User'),
                'datetime': _('Date/Time')
            }
            processors = {
                'user': 'format_user',
                'datetime': 'format_datetime'
            }
            structure_template = "datatableview/bootstrap_structure.html"

        def format_user(self, instance, **kwargs):
            url = reverse_lazy("chat:profile", kwargs={'email': instance.user_email})
            fieldValue = "<a href=\"#\" onclick=\"getModalInfo($(this), '0', 'general'); return false;\""
            fieldValue += "data-url='%s'>"%(url)
            fieldValue += instance.user
            fieldValue += "</a>"

            return fieldValue

        def get_action_name(self, instance, **kwargs):
            actions = {
                "access": _("Access"),
                "view": _("View"),
                "send": _("Send"),
                "create": _("Create"),
                "update": _("Update"),
                "start": _("Start"),
                "finish": _("Finish"),
                "answer": _("Answer"),
                "delete": _("Delete"),
                "create_post": _("Create Post"),
                "create_comment": _("Create Comment"),
                "edit_post": _("Edit Post"),
                "edit_comment": _("Edit Comment"),
                "set_goal": _("Set Goal"),
                "participate": _("Participate"),
                "remoe_account": _("Remove Account"),
                "watch": _("Watch"),
                "logout": _("Logout"),
                "view_statistics": _("View Statistics"),
                "view_new": _("View New"),
                "view_list_of_news": _("View List of News"),
                "view_history": _("View History"),
                "delete_post": _("Delete Post"),
                "delete_comment": _("Delete Comment"),
                "search": _("Search"),
                "change_password": _("Change Password"),
                "submit": _("Submit"),
                "click": _("Click"),
                "initwebconference": _("Init Webconference"),
                "participating": _("Participating"),
                "replicate": _("Replicate")
            }

            return actions.get(instance.action, instance.action)

        def get_area_name(self, instance, **kwargs):
            common = ['general', 'category', 'subject', 'message']

            elements = {
                "general_participants": _("General Participants"),
                "subject_participants": _("Subejct Participants"),
                "subject/resources": _("Subject/Resources"),
                "mural": _("Mural"),
                "post_comments": _("Post Comments"),
                "filelink": _("File link"),
                "pdffile": _("PDF File"),
                "webconference": _("Webconference"),
                "profile": _("Profile"),
                "user": _("Users"),
                "students_group": _("Students Group"),
                "pendencies": _("Pendencies"),
                "my_goals": _("My Goals"),
                "category": _("Category"),
                "subject": _("Subject"),
                "goals": _("Goals"),
                "news": _("News"),
                "system": _("System"),
                "ytvideo": _("Youtube Video"),
                "questionary": _("Questionary"),
                "Category_Dashboard": _("Category Analytics"),
                "Manager Dashboard": _("General Analytics"),
                "topic": _("Topic"),
                "questions_database": _("Questions Database"),
                "talk": _("Talk"),
                "chat": _("Chat"),
                "webpage": _("Webpage"),
                "links": _("Links"),
                "link": _("Links"),
                "analytics": _("Analytics")
            }

            if instance.resource in common:
                if instance.component == "mobile":
                    return elements.get("chat", None)

                return elements.get(instance.component, None)

            return elements.get(instance.resource, None)

        def format_datetime(self, instance, **kwargs):
            formatItem = get_format("DATETIME_INPUT_FORMATS")

            return timezone.localtime(instance.datetime).strftime(formatItem[0])

        def get_subject_name(self, instance, **kwargs):
            subject = instance.context.get("subject_name", None)
            subject_slug = instance.context.get("subject_slug", None)

            columnText = ''

            if not subject is None:
                url = reverse_lazy('subjects:view', kwargs={'slug': subject_slug})

                columnText = "<a href='%s' target='blank'>%s</a>"%(url, subject)

            return columnText

        def get_resource_name(self, instance, **kwargs):
            resourceTag = "%s_name"%(instance.resource)
            resourceIdTag = "%s_id"%(instance.resource)

            resource = instance.context.get(resourceTag, None)
            resource_id = instance.context.get(resourceIdTag, None)

            columnText = ''

            resQueryset = Resource.objects.filter(pk=resource_id)

            if not resource is None and instance.component == "resources" and resQueryset.exists():
                resourceObj = resQueryset.get()
            
                columnText = "<a href='%s' target='blank'>%s</a>"%(resourceObj.access_link(), resource)

            return columnText