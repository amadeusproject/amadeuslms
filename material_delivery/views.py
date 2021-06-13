""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import time
import json
import xlwt
import xlrd

from django.utils import timezone
from django.utils import formats

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

from pendencies.models import Pendencies, PendencyDone
from topics.models import Topic
from users.models import User

from .models import MaterialDelivery, StudentDeliver, TeacherEvaluation, valid_formats

from .forms import MaterialDeliveryForm, StudentMaterialForm, TeacherEvaluationForm, InlineSupportMaterialFormset

class DetailView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = "resources"
    log_action = "view"
    log_resource = "materialdelivery"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "material_delivery/view.html"
    model = MaterialDelivery

    context_object_name = "material_delivery"

    students = None
    studentDeliver = None

    def get_object(self):
        slug = self.kwargs.get("slug", "")
        material_delivery = get_object_or_404(MaterialDelivery, slug=slug)

        if has_subject_permissions(self.request.user, material_delivery.topic.subject):
            viewAsStudent = self.request.session.get(material_delivery.topic.subject.slug, False)

            if not viewAsStudent:
                if material_delivery.all_students:
                    self.students = User.objects.filter(
                        subject_student=material_delivery.topic.subject
                    ).order_by("username", "last_name")
                else:
                    self.students = User.objects.filter(
                        resource_students=material_delivery
                    ).order_by("username", "last_name")

                deliver = StudentDeliver.objects.filter(student = self.students.first())

                if deliver.exists():
                    self.studentDeliver = deliver.first()
        else:
            deliver = StudentDeliver.objects.filter(student = self.request.user)

            if deliver.exists():
                self.studentDeliver = deliver.first()
            else:
                self.studentDeliver = StudentDeliver.objects.create(delivery=material_delivery, student=self.request.user)

        return material_delivery

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        material_delivery = get_object_or_404(MaterialDelivery, slug=slug)

        if not has_resource_permissions(request.user, material_delivery):
            return redirect(reverse_lazy("subects:home"))

        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        template_name = "material_delivery/view.html"

        if self.object.show_window:
            template_name = "material_delivery/window_view.html"

        return template_name

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        material_delivery = get_object_or_404(MaterialDelivery, slug=slug)

        user = request.POST.get("selected_student", None)

        self.object = material_delivery

        if has_subject_permissions(self.request.user, material_delivery.topic.subject):
            if material_delivery.all_students:
                self.students = User.objects.filter(
                    subject_student=material_delivery.topic.subject
                ).order_by("username", "last_name")
            else:
                self.students = User.objects.filter(
                    resource_students=material_delivery
                ).order_by("username", "last_name")

            if not user is None:
                deliver = StudentDeliver.objects.filter(student__email = user)

                if deliver.exists():
                    self.studentDeliver = deliver.first()
                else:
                    student = get_object_or_404(User, email=user)
                    self.studentDeliver = StudentDeliver.objects.create(delivery=material_delivery, student=student)

        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        context["title"] = self.object.name

        context["topic"] = self.object.topic
        context["subject"] = self.object.topic.subject

        context["studentDeliver"] = self.studentDeliver

        if not self.students is None:
            context["sub_students"] = self.students
            context["student"] = self.request.POST.get(
                "selected_student", self.students.first().email
            )

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
        self.log_context["materialdelivery_id"] = self.object.id
        self.log_context["materialdelivery_name"] = self.object.name
        self.log_context["materialdelivery_slug"] = self.object.slug
        self.log_context["timestamp_start"] = str(int(time.time()))

        super(DetailView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_component)

        self.request.session["log_id"] = Log.objects.latest("id").id

        return context

class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
    log_component = "resources"
    log_action = "create"
    log_resource = "materialdelivery"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "material_delivery/create.html"
    form_class = MaterialDeliveryForm

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        topic = get_object_or_404(Topic, slug=slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        support_materials_form = InlineSupportMaterialFormset()

        return self.render_to_response(
            self.get_context_data(form=form, support_materials_form=support_materials_form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        support_materials_form = InlineSupportMaterialFormset(request.POST, request.FILES)

        if form.is_valid() and support_materials_form.is_valid():
            return self.form_valid(form, support_materials_form)
        else:
            return self.form_invalid(form, support_materials_form)

    def form_invalid(self, form, support_materials_form):
        return self.render_to_response(
            self.get_context_data(form=form, support_materials_form=support_materials_form)
        )

    def form_valid(self, form, support_materials_form):
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
        pendency.action = "submit"
        pendency.begin_date = self.object.data_ini
        pendency.end_date = self.object.data_end
        pendency.limit_date = self.object.data_end
        pendency.resource = self.object

        pendency.save()

        support_materials_form.instance = self.object
        support_materials_form.save(commit=False)

        for mform in support_materials_form.forms:
            msform = mform.save(commit=True)

            if msform.file is None:
                msform.delete()

        self.log_context["category_id"] = self.object.topic.subject.category.id
        self.log_context["category_name"] = self.object.topic.subject.category.name
        self.log_context["category_slug"] = self.object.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.topic.subject.id
        self.log_context["subject_name"] = self.object.topic.subject.name
        self.log_context["subject_slug"] = self.object.topic.subject.slug
        self.log_context["topic_id"] = self.object.topic.id
        self.log_context["topic_name"] = self.object.topic.name
        self.log_context["topic_slug"] = self.object.topic.slug
        self.log_context["materialdelivery_id"] = self.object.id
        self.log_context["materialdelivery_name"] = self.object.name
        self.log_context["materialdelivery_slug"] = self.object.slug

        super(CreateView, self).createLog(
            self.request.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

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

        context["title"] = _("Create Material Delivery")

        slug = self.kwargs.get("slug", "")
        topic = get_object_or_404(Topic, slug=slug)

        context["topic"] = topic
        context["subject"] = topic.subject
        context["mimeTypes"] = valid_formats

        return context

    def get_success_url(self):
        messages.success(self.request, _("The Material Delivery %s was successfully created in the topic %s!") % (self.object.name, self.object.topic.name))

        success_url = reverse_lazy("material_delivery:view", kwargs={"slug": self.object.slug})

        return success_url

class UpdateView(LoginRequiredMixin, LogMixin, generic.edit.UpdateView):
    log_component = "resources"
    log_action = "update"
    log_resource = "materialdelivery"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "material_delivery/update.html"

    model = MaterialDelivery
    form_class = MaterialDeliveryForm

    context_object_name = "material_delivery"

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("topic_slug", "")
        topic = get_object_or_404(Topic, slug=slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        support_materials_form = InlineSupportMaterialFormset(instance=self.object)

        return self.render_to_response(
            self.get_context_data(form=form, support_materials_form=support_materials_form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        support_materials_form = InlineSupportMaterialFormset(request.POST, request.FILES, instance=self.object)

        if form.is_valid() and support_materials_form.is_valid():
            return self.form_valid(form, support_materials_form)
        else:
            return self.form_invalid(form, support_materials_form)

    def form_invalid(self, form, support_materials_form):
        return self.render_to_response(
            self.get_context_data(form=form, support_materials_form=support_materials_form)
        )

    def form_valid(self, form, support_materials_form):
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
            pendency.action = "submit"
            pendency.begin_date = self.object.data_ini
            pendency.end_date = self.object.data_end
            pendency.limit_date = self.object.data_end
            pendency.resource = self.object

        pendency.save()

        support_materials_form.instance = self.object
        support_materials_form.save(commit=False)

        for mform in support_materials_form.forms:
            msform = mform.save(commit=True)

            if msform.file is None:
                msform.delete()
        
        for item in support_materials_form.deleted_objects:
            item.delete()

        self.log_context["category_id"] = self.object.topic.subject.category.id
        self.log_context["category_name"] = self.object.topic.subject.category.name
        self.log_context["category_slug"] = self.object.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.topic.subject.id
        self.log_context["subject_name"] = self.object.topic.subject.name
        self.log_context["subject_slug"] = self.object.topic.subject.slug
        self.log_context["topic_id"] = self.object.topic.id
        self.log_context["topic_name"] = self.object.topic.name
        self.log_context["topic_slug"] = self.object.topic.slug
        self.log_context["materialdelivery_id"] = self.object.id
        self.log_context["materialdelivery_name"] = self.object.name
        self.log_context["materialdelivery_slug"] = self.object.slug

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

        context["title"] = _("Update Material Delivery")

        slug = self.kwargs.get("topic_slug", "")
        topic = get_object_or_404(Topic, slug=slug)

        context["topic"] = topic
        context["subject"] = topic.subject
        context["mimeTypes"] = valid_formats

        return context

    def get_success_url(self):
        messages.success(self.request, _("The Material Delivery %s of the topic %s was updated successfully!") % (self.object.name, self.object.topic.name))

        success_url = reverse_lazy("material_delivery:view", kwargs={"slug": self.object.slug})

        return success_url

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
    log_component = "resources"
    log_action = "delete"
    log_resource = "materialdelivery"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "resources/delete.html"
    model = MaterialDelivery
    context_object_name = "resource"

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", "")
        material_delivery = get_object_or_404(MaterialDelivery, slug=slug)

        if not has_subject_permissions(request.user, material_delivery.topic.subject):
            return redirect(reverse_lazy("subjects:home"))

        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(
            self.request,
            _("The material delivery %s of the topic %s was removed successfully!")
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
        self.log_context["materialdelivery_id"] = self.object.id
        self.log_context["materialdelivery_name"] = self.object.name
        self.log_context["materialdelivery_slug"] = self.object.slug

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

class StudentMaterialCreate(LoginRequiredMixin, LogMixin, generic.CreateView):
    log_component = "resources"
    log_action = "submit"
    log_resource = "materialdelivery"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "material_delivery/_student_form.html"
    form_class = StudentMaterialForm

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get("deliver", 0)
        deliver = get_object_or_404(StudentDeliver, pk=pk)

        if not has_resource_permissions(request.user, deliver.delivery):
            return JsonResponse({"status": 403, "message": _("You don't have permission to submit files in this delivery")})

        todaysDate = timezone.localtime(timezone.now())

        if timezone.localtime(deliver.delivery.data_ini) > todaysDate:
            return JsonResponse({"status": 500, "message": _("This resource can only be accessed after %s"%(formats.date_format(timezone.localtime(deliver.delivery.data_ini), "SHORT_DATETIME_FORMAT")))})
        elif timezone.localtime(deliver.delivery.data_end) < todaysDate:
            return JsonResponse({"status": 500, "message": _("The material could be delivered only until %s"%(formats.date_format(timezone.localtime(deliver.delivery.data_end), "SHORT_DATETIME_FORMAT")))})

        return super(StudentMaterialCreate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit = False)

        pk = self.kwargs.get("deliver", 0)
        deliver = get_object_or_404(StudentDeliver, pk=pk)

        self.object.deliver = deliver

        self.object.save()

        self.log_context["category_id"] = self.object.deliver.delivery.topic.subject.category.id
        self.log_context["category_name"] = self.object.deliver.delivery.topic.subject.category.name
        self.log_context["category_slug"] = self.object.deliver.delivery.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.deliver.delivery.topic.subject.id
        self.log_context["subject_name"] = self.object.deliver.delivery.topic.subject.name
        self.log_context["subject_slug"] = self.object.deliver.delivery.topic.subject.slug
        self.log_context["topic_id"] = self.object.deliver.delivery.topic.id
        self.log_context["topic_name"] = self.object.deliver.delivery.topic.name
        self.log_context["topic_slug"] = self.object.deliver.delivery.topic.slug
        self.log_context["materialdelivery_id"] = self.object.deliver.delivery.id
        self.log_context["materialdelivery_name"] = self.object.deliver.delivery.name
        self.log_context["materialdelivery_slug"] = self.object.deliver.delivery.slug
        self.log_context["materialdelivery_deliver"] = self.object.deliver.id
        self.log_context["materialdelivery_material"] = self.object.id

        super(StudentMaterialCreate, self).createLog(
            self.request.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        newMaterial = render_to_string(
                "material_delivery/_student_material_view.html", {"material": self.object}, self.request
            )

        return JsonResponse({"status": 200, "content": newMaterial, "message": _("Material submited successfully!")})

    def get_context_data(self, **kwargs):
        context = super(StudentMaterialCreate, self).get_context_data(**kwargs)

        context["deliver_pk"] = self.kwargs.get("deliver", 0)
        context["mimeTypes"] = valid_formats

        return context

class TeacherEvaluate(LoginRequiredMixin, LogMixin, generic.CreateView):
    log_component = "resources"
    log_action = "evaluate"
    log_resource = "materialdelivery"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "material_delivery/_teacher_form.html"
    form_class = TeacherEvaluationForm

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get("deliver", 0)
        deliver = get_object_or_404(StudentDeliver, pk=pk)

        if not has_resource_permissions(request.user, deliver.delivery):
            return JsonResponse({"status": 403, "message": _("You don't have permission to evaluate this delivery")})

        return super(TeacherEvaluate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit = False)

        pk = self.kwargs.get("deliver", 0)
        deliver = get_object_or_404(StudentDeliver, pk=pk)

        self.object.deliver = deliver
        self.object.teacher = self.request.user

        self.object.save()

        self.log_context["category_id"] = self.object.deliver.delivery.topic.subject.category.id
        self.log_context["category_name"] = self.object.deliver.delivery.topic.subject.category.name
        self.log_context["category_slug"] = self.object.deliver.delivery.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.deliver.delivery.topic.subject.id
        self.log_context["subject_name"] = self.object.deliver.delivery.topic.subject.name
        self.log_context["subject_slug"] = self.object.deliver.delivery.topic.subject.slug
        self.log_context["topic_id"] = self.object.deliver.delivery.topic.id
        self.log_context["topic_name"] = self.object.deliver.delivery.topic.name
        self.log_context["topic_slug"] = self.object.deliver.delivery.topic.slug
        self.log_context["materialdelivery_id"] = self.object.deliver.delivery.id
        self.log_context["materialdelivery_name"] = self.object.deliver.delivery.name
        self.log_context["materialdelivery_slug"] = self.object.deliver.delivery.slug
        self.log_context["materialdelivery_deliver"] = self.object.deliver.id

        super(TeacherEvaluate, self).createLog(
            self.request.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        newMaterial = render_to_string(
                "material_delivery/_teacher_evaluation_view.html", {"evaluation": self.object}, self.request
            )

        return JsonResponse({"status": 200, "content": newMaterial, "message": _("Delivery evaluated successfully!")})

    def get_context_data(self, **kwargs):
        context = super(TeacherEvaluate, self).get_context_data(**kwargs)

        context["deliver_pk"] = self.kwargs.get("deliver", 0)
        context["mimeTypes"] = valid_formats
        context["form_url"] = reverse_lazy("material_delivery:evaluate", kwargs={"deliver": context["deliver_pk"]})

        return context

class TeacherUpdateEvaluation(LoginRequiredMixin, LogMixin, generic.UpdateView):
    log_component = "resources"
    log_action = "evaluate_update"
    log_resource = "materialdelivery"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "material_delivery/_teacher_form.html"
    form_class = TeacherEvaluationForm
    model = TeacherEvaluation

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get("deliver", 0)
        deliver = get_object_or_404(StudentDeliver, pk=pk)

        if not has_resource_permissions(request.user, deliver.delivery):
            return JsonResponse({"status": 403, "message": _("You don't have permission to evaluate this delivery")})

        return super(TeacherUpdateEvaluation, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit = False)

        pk = self.kwargs.get("deliver", 0)
        deliver = get_object_or_404(StudentDeliver, pk=pk)

        self.object.deliver = deliver
        self.object.teacher = self.request.user
        self.object.is_updated = True

        self.object.save()

        self.log_context["category_id"] = self.object.deliver.delivery.topic.subject.category.id
        self.log_context["category_name"] = self.object.deliver.delivery.topic.subject.category.name
        self.log_context["category_slug"] = self.object.deliver.delivery.topic.subject.category.slug
        self.log_context["subject_id"] = self.object.deliver.delivery.topic.subject.id
        self.log_context["subject_name"] = self.object.deliver.delivery.topic.subject.name
        self.log_context["subject_slug"] = self.object.deliver.delivery.topic.subject.slug
        self.log_context["topic_id"] = self.object.deliver.delivery.topic.id
        self.log_context["topic_name"] = self.object.deliver.delivery.topic.name
        self.log_context["topic_slug"] = self.object.deliver.delivery.topic.slug
        self.log_context["materialdelivery_id"] = self.object.deliver.delivery.id
        self.log_context["materialdelivery_name"] = self.object.deliver.delivery.name
        self.log_context["materialdelivery_slug"] = self.object.deliver.delivery.slug
        self.log_context["materialdelivery_deliver"] = self.object.deliver.id

        super(TeacherUpdateEvaluation, self).createLog(
            self.request.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        newMaterial = render_to_string(
                "material_delivery/_teacher_evaluation_view.html", {"evaluation": self.object, "deliver_pk": pk, "user": self.object.teacher}, self.request
            )

        return JsonResponse({"status": 200, "content": newMaterial, "message": _("Evaluation updated successfully!")})

    def get_context_data(self, **kwargs):
        context = super(TeacherUpdateEvaluation, self).get_context_data(**kwargs)

        context["deliver_pk"] = self.kwargs.get("deliver", 0)
        context["mimeTypes"] = valid_formats
        context["form_url"] = reverse_lazy("material_delivery:evaluate_update", kwargs={"deliver": context["deliver_pk"], "pk": self.object.pk})

        return context