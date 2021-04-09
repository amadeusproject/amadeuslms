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

from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import JsonResponse, HttpResponse

from amadeus.permissions import has_subject_permissions, has_resource_permissions

from log.models import Log
from log.mixins import LogMixin

from topics.models import Topic
from pendencies.models import Pendencies, PendencyDone

from .models import H5P
from .forms import H5PForm

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

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.students.count() <= 0:
            self.object.all_students = True
        else:
            self.object.all_students = False

        if not self.object.topic.visible and not self.object.topic.repository:
            self.object.visible = False

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
    log_component = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    model = H5P
    template_name = "h5p/relatorios.html"

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        h5p = get_object_or_404(H5P, slug=slug)

        if not has_subject_permissions(request.user, h5p.topic.subejct):
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

        slug = self.kwargs.get("slug", "")
        h5p = get_object_or_404(H5P, slug=slug)

        date_format = ("%d/%m/%Y %H:%M" if self.request.GET.get("language", "") == "pt-br" else "%m/%d/%Y %I:%M %p")

        return context

def class_results(request, slug):
    h5p = get_object_or_404(H5P, slug=slug)
    number_questions = 0

    data = []

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
    worksheet.write(0, 2, u"Questões Respondidas")
    worksheet.write(0, 3, u"Questões Corretas")
    worksheet.write(0, 4, u"% Acerto")

    line = 1

    
    path1 = os.path.join(settings.BASE_DIR, "h5p")
    path2 = os.path.join(path1, "sheets")
    path3 = os.path.join(path2, "xls")

    filename = str(questionary.slug) + ".xls"
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
