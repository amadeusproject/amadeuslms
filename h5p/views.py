""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import json
import time
import xlwt
import xlrd

from django.db.models import Q
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

from django.http import JsonResponse, HttpResponse

from amadeus.permissions import has_subject_permissions, has_resource_permissions

from log.decorators import log_decorator
from log.models import Log
from log.mixins import LogMixin

from webpage.forms import FormModalMessage

from chat.models import Conversation, TalkMessages, ChatVisualizations

from topics.models import Topic
from pendencies.models import Pendencies, PendencyDone

from .models import H5P, h5p_contents, UserScores
from .forms import H5PForm
from .base_plugin.module import *

class DetailView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = "resources"
    log_action = "view"
    log_resource = "h5p"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "h5p/view.html"
    model = H5P

    context_object_name = "h5p"

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        h5p = get_object_or_404(H5P, slug=slug)

        if not has_resource_permissions(request.user, h5p):
            return redirect(reverse_lazy("subects:home"))

        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        template_name = "h5p/view.html"

        if self.object.show_window:
            template_name = "h5p/window_view.html"

        return template_name

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        if self.object.h5p_resource:
            _mutable = self.request.GET._mutable

            self.request.GET._mutable = True

            self.request.GET['contentId'] = str(self.object.h5p_resource.content_id)
            self.request.GET['embed_type'] = "div"

            self.request.GET._mutable = _mutable

            h5pLoad(self.request)
            content = includeH5p(self.request)
            context["h5p_html"] = content["html"]
            context["data"] = content["data"]

        context["title"] = self.object.name

        context["topic"] = self.object.topic
        context["subject"] = self.object.topic.subject

        context['studentView'] = self.request.session.get(self.object.topic.subject.slug, False)

        self.log_context["category_id"] = self.object.topic.subject.category.id
        self.log_context["category_name"] = self.object.topic.subject.category.name
        self.log_context["category_slug"] = self.object.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.topic.subject.id
        self.log_context["subject_name"] = self.object.topic.subject.name
        self.log_context["subject_slug"] = self.object.topic.subject.slug
        self.log_context["topic_id"] = self.object.topic.id
        self.log_context["topic_name"] = self.object.topic.name
        self.log_context["topic_slug"] = self.object.topic.slug
        self.log_context["h5p_id"] = self.object.id
        self.log_context["h5p_name"] = self.object.name
        self.log_context["h5p_slug"] = self.object.slug
        self.log_context["timestamp_start"] = str(int(time.time()))

        super(DetailView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_component)

        self.request.session["log_id"] = Log.objects.latest("id").id

        return context

class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
    log_component = "resources"
    log_action = "create"
    log_resource = "h5p"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "h5p/create.html"
    form_class = H5PForm

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        topic = get_object_or_404(Topic, slug=slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})

        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)

        slug = self.kwargs.get("slug", "")
        topic = get_object_or_404(Topic, slug=slug)

        self.object.topic = topic
        self.object.order = topic.resource_topic.count() + 1

        if self.object.students.count() <= 0:
            self.object.all_students = True
        else:
            self.object.all_students = False

        if not self.object.topic.visible and not self.object.topic.repository:
            self.object.visible = False

        if "file_uploaded" in self.request.POST:
            print(self.request.POST)
            
            contentResource = h5p_contents.objects.all().order_by('-content_id')[0]

            self.object.h5p_resource = contentResource

        self.object.save()

        pendency = Pendencies()
        pendency.action = "finish"
        pendency.begin_date = self.object.data_ini
        pendency.end_date = self.object.data_end
        pendency.limit_date = self.object.data_end
        pendency.resource = self.object

        pendency.save()

        self.log_context["category_id"] = self.object.topic.subject.category.id
        self.log_context["category_name"] = self.object.topic.subject.category.name
        self.log_context["category_slug"] = self.object.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.topic.subject.id
        self.log_context["subject_name"] = self.object.topic.subject.name
        self.log_context["subject_slug"] = self.object.topic.subject.slug
        self.log_context["topic_id"] = self.object.topic.id
        self.log_context["topic_name"] = self.object.topic.name
        self.log_context["topic_slug"] = self.object.topic.slug
        self.log_context["h5p_id"] = self.object.id
        self.log_context["h5p_name"] = self.object.name
        self.log_context["h5p_slug"] = self.object.slug

        super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_initial(self):
        initial = super(CreateView, self).get_initial()

        slug = self.kwargs.get("slug", "")

        topic = get_object_or_404(Topic, slug=slug)
        initial["subject"] = topic.subject
        initial["topic"] = topic

        return initial

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)

        context["title"] = _("Create H5P")

        slug = self.kwargs.get("slug", "")
        topic = get_object_or_404(Topic, slug=slug)

        context["topic"] = topic
        context["subject"] = topic.subject

        return context

    def get_success_url(self):
        messages.success(self.request, _("The H5P %s was successfully created in the topic %s!") % (self.object.name, self.object.topic.name))

        success_url = reverse_lazy("h5p:view", kwargs={"slug": self.object.slug})

        return success_url

class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    log_component = "resources"
    log_action = "update"
    log_resource = "h5p"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "h5p/update.html"
    model = H5P
    form_class = H5PForm
    context_object_name = "resource"

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("topic_slug", "")
        topic = get_object_or_404(Topic, slug=slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})

        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.students.count() <= 0:
            self.object.all_students = True
        else:
            self.object.all_students = False

        if not self.object.topic.visible and not self.object.topic.repository:
            self.object.visible = False

        if "file_uploaded" in self.request.POST:
            print(self.request.POST)
            
            contentResource = h5p_contents.objects.all().order_by('-content_id')[0]

            self.object.h5p_resource = contentResource

        self.object.save()

        pendency = Pendencies.objects.filter(resource=self.object).first()

        if not pendency is None:
            pendency.begin_date = self.object.data_ini
            pendency.end_date = self.object.data_end
            pendency.limit_date = self.object.data_end
        else:
            pendency = Pendencies()
            pendency.action = "finish"
            pendency.begin_date = self.object.data_ini
            pendency.end_date = self.object.data_end
            pendency.limit_date = self.object.data_end
            pendency.resource = self.object

        pendency.save()

        self.log_context["category_id"] = self.object.topic.subject.category.id
        self.log_context["category_name"] = self.object.topic.subject.category.name
        self.log_context["category_slug"] = self.object.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.topic.subject.id
        self.log_context["subject_name"] = self.object.topic.subject.name
        self.log_context["subject_slug"] = self.object.topic.subject.slug
        self.log_context["topic_id"] = self.object.topic.id
        self.log_context["topic_name"] = self.object.topic.name
        self.log_context["topic_slug"] = self.object.topic.slug
        self.log_context["h5p_id"] = self.object.id
        self.log_context["h5p_name"] = self.object.name
        self.log_context["h5p_slug"] = self.object.slug

        super(UpdateView, self).createLog(
            self.request.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        context["title"] = _("Update H5P")

        slug = self.kwargs.get("topic_slug", "")
        topic = get_object_or_404(Topic, slug=slug)

        context["topic"] = topic
        context["subject"] = topic.subject

        return context

    def get_success_url(self):
        messages.success(self.request, _("The H5P %s of the topic %s was updated successfully!") % (self.object.name, self.object.topic.name))

        success_url = reverse_lazy("h5p:view", kwargs={"slug": self.object.slug})

        return success_url

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
    log_component = "resources"
    log_action = "delete"
    log_resource = "h5p"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "resources/delete.html"
    model = H5P
    context_object_name = "resource"

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        h5p = get_object_or_404(H5P, slug=slug)

        if not has_subject_permissions(request.user, h5p.topic.subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(
            self.request,
            _("The H5P %s of the topic %s was removed successfully!")
            % (self.object.name, self.object.topic.name),
        )

        self.object.h5p_resource.delete()

        self.log_context["category_id"] = self.object.topic.subject.category.id
        self.log_context["category_name"] = self.object.topic.subject.category.name
        self.log_context["category_slug"] = self.object.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.topic.subject.id
        self.log_context["subject_name"] = self.object.topic.subject.name
        self.log_context["subject_slug"] = self.object.topic.subject.slug
        self.log_context["topic_id"] = self.object.topic.id
        self.log_context["topic_name"] = self.object.topic.name
        self.log_context["topic_slug"] = self.object.topic.slug
        self.log_context["h5p_id"] = self.object.id
        self.log_context["h5p_name"] = self.object.name
        self.log_context["h5p_slug"] = self.object.slug

        super(DeleteView, self).createLog(
            self.request.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        return reverse_lazy(
            "subjects:view", kwargs={"slug": self.object.topic.subject.slug}
        )

class StatisticsView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = "resources"
    log_action = "view_statistics"
    log_resource = "h5p"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    model = H5P
    template_name = "h5p/relatorios.html"

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        h5p = get_object_or_404(H5P, slug=slug)

        if not has_subject_permissions(request.user, h5p.topic.subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(StatisticsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatisticsView, self).get_context_data(**kwargs)

        self.log_context["category_id"] = self.object.topic.subject.category.id
        self.log_context["category_name"] = self.object.topic.subject.category.name
        self.log_context["category_slug"] = self.object.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.topic.subject.id
        self.log_context["subject_name"] = self.object.topic.subject.name
        self.log_context["subject_slug"] = self.object.topic.subject.slug
        self.log_context["topic_id"] = self.object.topic.id
        self.log_context["topic_name"] = self.object.topic.name
        self.log_context["topic_slug"] = self.object.topic.slug
        self.log_context["h5p_id"] = self.object.id
        self.log_context["h5p_name"] = self.object.name
        self.log_context["h5p_slug"] = self.object.slug

        super(StatisticsView, self).createLog(
            self.request.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        context["title"] = _("H5P Reports")

        slug = self.kwargs.get("slug")
        h5p = get_object_or_404(H5P, slug=slug)

        date_format = (
            "%d/%m/%Y %H:%M"
            if self.request.GET.get("language", "") == "pt-br"
            else "%m/%d/%Y %I:%M %p"
        )

        if self.request.GET.get("language", "") == "":
            start_date = datetime.now() - timedelta(30)
            end_date = datetime.now()
        else:
            start_date = datetime.strptime(
                self.request.GET.get("init_date", ""), date_format
            )
            end_date = datetime.strptime(
                self.request.GET.get("end_date", ""), date_format
            )

        context["init_date"] = start_date
        context["end_date"] = end_date

        alunos = h5p.students.all()

        if h5p.all_students:
            alunos = h5p.topic.subject.students.all()

        vis_ou = Log.objects.filter(
            context__contains={"h5p_id": h5p.id},
            resource="h5p",
            user_email__in=(aluno.email for aluno in alunos),
            datetime__range=(start_date, end_date + timedelta(minutes=1)),
        ).filter(Q(action="view") | Q(action="finish") | Q(action="start"))

        did, n_did, history = (
            str(_("Realized")),
            str(_("Unrealized")),
            str(_("Historic")),
        )
        re = []
        data_n_did, data_history = [], []
        json_n_did, json_history = {}, {}

        for log_al in vis_ou.order_by("datetime"):
            if log_al.action == "view":
                if any(log_al.user in x for x in data_history):
                    continue
            elif log_al.action == "finish":
                index = None

                for dh in data_history:
                    if log_al.user in dh:
                        index = dh
                        break

                if not index is None:
                    data_history.remove(index)

            data_history.append(
                [
                    log_al.user,
                    ", ".join(
                        [
                            str(x)
                            for x in h5p.topic.subject.group_subject.filter(
                                participants__email=log_al.user_email
                            )
                        ]
                    ),
                    log_al.action,
                    log_al.datetime,
                ]
            )

        json_history["data"] = data_history

        not_view = alunos.exclude(
            email__in=[
                log.user_email
                for log in vis_ou.filter(action="view").distinct("user_email")
            ]
        )
        index = 0
        for alun in not_view:
            data_n_did.append(
                [
                    index,
                    str(alun),
                    ", ".join(
                        [
                            str(x)
                            for x in h5p.topic.subject.group_subject.filter(
                                participants__email=alun.email
                            )
                        ]
                    ),
                    str(_("View")),
                    str(alun.email),
                ]
            )
            index += 1

        not_start = alunos.exclude(
            email__in=[
                log.user_email
                for log in vis_ou.filter(action="start").distinct("user_email")
            ]
        )
        for alun in not_start:
            data_n_did.append(
                [
                    index,
                    str(alun),
                    ", ".join(
                        [
                            str(x)
                            for x in h5p.topic.subject.group_subject.filter(
                                participants__email=alun.email
                            )
                        ]
                    ),
                    str(_("Start")),
                    str(alun.email),
                ]
            )
            index += 1

        not_finish = alunos.exclude(
            email__in=[
                log.user_email
                for log in vis_ou.filter(action="finish").distinct("user_email")
            ]
        )
        for alun in not_finish:
            data_n_did.append(
                [
                    index,
                    str(alun),
                    ", ".join(
                        [
                            str(x)
                            for x in h5p.topic.subject.group_subject.filter(
                                participants__email=alun.email
                            )
                        ]
                    ),
                    str(_("Finish")),
                    str(alun.email),
                ]
            )
            index += 1

        json_n_did["data"] = data_n_did

        context["json_n_did"] = json_n_did
        context["json_history"] = json_history

        c_visualizou = vis_ou.filter(action="view").distinct("user_email").count()
        c_start = vis_ou.filter(action="start").distinct("user_email").count()
        c_finish = vis_ou.filter(action="finish").distinct("user_email").count()

        column_view = str(_("View"))
        column_start = str(_("Start"))
        column_finish = str(_("Finish"))

        re.append([str(_("H5P")), did, n_did])
        re.append([column_view, c_visualizou, alunos.count() - c_visualizou])
        re.append([column_start, c_start, alunos.count() - c_start])
        re.append([column_finish, c_finish, alunos.count() - c_finish])

        context["topic"] = h5p.topic
        context["subject"] = h5p.topic.subject
        context["db_data"] = re
        context["title_chart"] = _("Actions about resource")
        context["title_vAxis"] = _("Quantity")
        context["view"] = column_view
        context["start"] = column_start
        context["finish"] = column_finish
        context["n_did_table"] = n_did
        context["did_table"] = did
        context["history_table"] = history

        return context

class SendMessage(LoginRequiredMixin, LogMixin, generic.edit.FormView):
    log_component = "resources"
    log_action = "send"
    log_resource = "h5p"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "h5p/send_message.html"
    form_class = FormModalMessage

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        h5p = get_object_or_404(H5P, slug=slug)
        self.h5p = h5p

        if not has_subject_permissions(request.user, h5p.topic.subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(SendMessage, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        message = form.cleaned_data.get("comment")
        image = form.cleaned_data.get("image", "")
        users = (self.request.POST.get("users[]", "")).split(",")
        user = self.request.user
        subject = self.h5p.topic.subject

        if users[0] != "":
            for u in users:
                to_user = User.objects.get(email=u)
                talk, create = Conversation.objects.get_or_create(
                    user_one=user, user_two=to_user
                )
                created = TalkMessages.objects.create(
                    text=message, talk=talk, user=user, subject=subject, image=image
                )

                simple_notify = textwrap.shorten(
                    strip_tags(message), width=30, placeholder="..."
                )

                if image != "":
                    simple_notify += " ".join(_("[Photo]"))

                notification = {
                    "type": "chat",
                    "subtype": "subject",
                    "space": subject.slug,
                    "user_icon": created.user.image_url,
                    "notify_title": str(created.user),
                    "simple_notify": simple_notify,
                    "view_url": reverse(
                        "chat:view_message", args=(created.id,), kwargs={}
                    ),
                    "complete": render_to_string(
                        "chat/_message.html", {"talk_msg": created}, self.request
                    ),
                    "container": "chat-" + str(created.user.id),
                    "last_date": _("Last message in %s")
                    % (
                        formats.date_format(
                            created.create_date, "SHORT_DATETIME_FORMAT"
                        )
                    ),
                }

                notification = json.dumps(notification)

                Group("user-%s" % to_user.id).send({"text": notification})

                ChatVisualizations.objects.create(
                    viewed=False, message=created, user=to_user
                )

            success = str(_("The message was successfull sent!"))
            return JsonResponse({"message": success})

        erro = HttpResponse(str(_("No user selected!")))
        erro.status_code = 404
        return erro

    def get_context_data(self, **kwargs):
        context = super(SendMessage, self).get_context_data()
        context["h5p"] = get_object_or_404(
            H5P, slug=self.kwargs.get("slug", "")
        )
        return context

def class_results(request, slug):
    h5p = get_object_or_404(H5P, slug=slug)

    results = UserScores.objects.filter(h5p_component = h5p).order_by("student__username", "student__last_name", "-interaction_date")

    if h5p.all_students:
        students = User.objects.filter(
            subject_student=h5p.topic.subject
        ).order_by("username", "last_name")
    else:
        students = User.objects.filter(resource_students=h5p).order_by(
            "username", "last_name"
        )

    data = []

    appeared = []

    for result in results:
        if result.student in students:
            appeared.append(result.student.email)

        line = {}

        line["student"] = result.student.fullname

        if result.max_score > 0:
            percentage = (result.score / result.max_score) * 100
        else:
            percentage = 0

        line["total_questions"] = result.max_score
        line["total_correct"] = result.score

        line["percentage"] = percentage

        data.append(line)

    students = students.exclude(email__in=appeared)

    for student in students:
        line = {}

        line["student"] = student.fullname
        line["total_questions"] = "-"
        line["total_correct"] = "-"
        line["percentage"] = 0

        data.append(line)

    html = render_to_string(
        "h5p/_results.html", {"data": data, "h5p": h5p}
    )
    return JsonResponse({"result": html})


def results_sheet(request, slug):
    h5p = get_object_or_404(H5P, slug=slug)
    number_questions = 0

    data = []
        
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u"Resultados do H5P")
    worksheet.write(0, 0, u"Estudante")
    worksheet.write(0, 1, u"Total de Questões")
    worksheet.write(0, 2, u"Questões Corretas")
    worksheet.write(0, 3, u"% Acerto")

    line = 1

    results = UserScores.objects.filter(h5p_component = h5p).order_by("student__username", "student__last_name", "-interaction_date")

    if h5p.all_students:
        students = User.objects.filter(
            subject_student=h5p.topic.subject
        ).order_by("username", "last_name")
    else:
        students = User.objects.filter(resource_students=h5p).order_by(
            "username", "last_name"
        )

    appeared = []

    for result in results:
        if result.student in students:
            appeared.append(result.student.email)

        worksheet.write(line, 0, result.student.fullname())

        if result.max_score > 0:
            percentage = (result.score / result.max_score) * 100
        else:
            percentage = 0

        worksheet.write(line, 1, result.max_score)
        worksheet.write(line, 2, result.score)
        worksheet.write(line, 3, percentage)

        line = line + 1

    students = students.exclude(email__in=appeared)

    for student in students:
        worksheet.write(line, 0, student.fullname())
        worksheet.write(line, 1, "-")
        worksheet.write(line, 2, "-")
        worksheet.write(line, 3, 0)

        line = line + 1

    path1 = os.path.join(settings.BASE_DIR, "h5p")
    path2 = os.path.join(path1, "sheets")
    path3 = os.path.join(path2, "xls")

    filename = str(h5p.slug) + ".xls"
    folder_path = os.path.join(path3, filename)

    # check if the folder already exists
    if not os.path.isdir(path3):
        os.makedirs(path3)

    workbook.save(folder_path)

    filepath = os.path.join(
        "h5p", os.path.join("sheets", os.path.join("xls", filename))
    )

    if not os.path.exists(filepath):
        raise Http404()

    response = HttpResponse(open(filepath, "rb").read())
    response["Content-Type"] = "application/force-download"
    response["Pragma"] = "public"
    response["Expires"] = "0"
    response["Cache-Control"] = "must-revalidate, post-check=0, pre-check=0"
    response["Content-Disposition"] = "attachment; filename=%s" % (filename)
    response["Content-Transfer-Encoding"] = "binary"
    response["Content-Length"] = str(os.path.getsize(filepath))

    return response

@csrf_exempt
@log_decorator("resources", "finish", "h5p")
def contentFinish(request):
    resource = get_object_or_404(H5P, h5p_resource = request.POST.get('contentId', 0))
    
    if not has_subject_permissions(request.user, resource.topic.subject):
        userScore = UserScores()
        userScore.h5p_component = resource
        userScore.student = request.user
        userScore.max_score = request.POST.get('maxScore', 0)
        userScore.score = request.POST.get('score', 0)

        userScore.save()

    request.log_context = {}
    request.log_context["category_id"] = resource.topic.subject.category.id
    request.log_context["category_name"] = resource.topic.subject.category.name
    request.log_context["category_slug"] = resource.topic.subject.category.slug
    request.log_context["subject_id"] = resource.topic.subject.id
    request.log_context["subject_name"] = resource.topic.subject.name
    request.log_context["subject_slug"] = resource.topic.subject.slug
    request.log_context["topic_id"] = resource.topic.id
    request.log_context["topic_name"] = resource.topic.name
    request.log_context["topic_slug"] = resource.topic.slug
    request.log_context["h5p_id"] = resource.id
    request.log_context["h5p_name"] = resource.name
    request.log_context["h5p_slug"] = resource.slug

    return JsonResponse({"message": "Finished content"})

@log_decorator("resources", "start", "h5p")
def contentStart(request, slug):
    resource = get_object_or_404(H5P, slug=slug)

    request.log_context = {}
    request.log_context["category_id"] = resource.topic.subject.category.id
    request.log_context["category_name"] = resource.topic.subject.category.name
    request.log_context["category_slug"] = resource.topic.subject.category.slug
    request.log_context["subject_id"] = resource.topic.subject.id
    request.log_context["subject_name"] = resource.topic.subject.name
    request.log_context["subject_slug"] = resource.topic.subject.slug
    request.log_context["topic_id"] = resource.topic.id
    request.log_context["topic_name"] = resource.topic.name
    request.log_context["topic_slug"] = resource.topic.slug
    request.log_context["h5p_id"] = resource.id
    request.log_context["h5p_name"] = resource.name
    request.log_context["h5p_slug"] = resource.slug

    return JsonResponse({"registered": True})