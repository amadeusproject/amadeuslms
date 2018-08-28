""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


# Create your views here.
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from amadeus.permissions import has_subject_permissions, has_resource_permissions
from .forms import PDFFileForm
from os import path
import datetime
from log.models import Log
from django.http import HttpResponse, Http404

from log.mixins import LogMixin
from topics.models import Topic, Resource
from .models import PDFFile, valid_formats
from pendencies.forms import PendenciesForm

from chat.models import Conversation, TalkMessages, ChatVisualizations
from users.models import User
from subjects.models import Subject
from webpage.forms import FormModalMessage
from django.http import JsonResponse

from django.template.loader import render_to_string
from django.utils import formats
import textwrap
from django.utils.html import strip_tags
import json
from channels import Group


class ViewPDFFile(LoginRequiredMixin, LogMixin, generic.TemplateView):
    template_name='pdf_file/view.html'
    log_component = 'resources'
    log_action = 'view'
    log_resource = 'pdffile'
    log_context = {}
    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        resource = get_object_or_404(Resource, slug = slug)
        topic = resource.topic

        if not has_subject_permissions(request.user, topic.subject) and not has_resource_permissions(request.user, resource):
            return redirect(reverse_lazy('subjects:home'))

        return super(ViewPDFFile, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewPDFFile, self).get_context_data(**kwargs)
        slug = self.kwargs.get('slug', '')
        pdf_file = PDFFile.objects.get(slug=slug)
        
        context['pdf_file'] = pdf_file
        context['absolute_url'] = self.request.build_absolute_uri(pdf_file.file.url)
        context['subject'] = pdf_file.topic.subject

        self.log_context['category_id'] = pdf_file.topic.subject.category.id
        self.log_context['category_name'] = pdf_file.topic.subject.category.name
        self.log_context['category_slug'] = pdf_file.topic.subject.category.slug
        self.log_context['subject_id'] = pdf_file.topic.subject.id
        self.log_context['subject_name'] = pdf_file.topic.subject.name
        self.log_context['subject_slug'] = pdf_file.topic.subject.slug
        self.log_context['topic_id'] = pdf_file.topic.id
        self.log_context['topic_name'] = pdf_file.topic.name
        self.log_context['topic_slug'] = pdf_file.topic.slug
        self.log_context['pdffile_id'] = pdf_file.id
        self.log_context['pdffile_name'] = pdf_file.name
        self.log_context['pdffile_slug'] = pdf_file.slug

        super(ViewPDFFile, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return context


    def render_to_response(self, context, **response_kwargs):
        slug = self.kwargs.get('slug', '')
        pdf_file = PDFFile.objects.get(slug=slug)

        if not path.exists(pdf_file.file.path):
            raise Http404()
        
        if pdf_file.show_window:
            response = HttpResponse(open(pdf_file.file.path, 'rb').read(),content_type = 'application/pdf')
            return response


        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
        request = self.request,
        template = self.get_template_names(),
        context = context,
        **response_kwargs
        )

class PDFFileCreateView(LoginRequiredMixin, LogMixin , generic.CreateView):
    form_class = PDFFileForm
    template_name = 'pdf_file/create.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    log_component = 'resources'
    log_resource = 'pdffile'
    log_action = 'create'
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(PDFFileCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        pendencies_form = PendenciesForm(initial = {'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize"))]})

        return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

    def post(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        pendencies_form = PendenciesForm(self.request.POST, initial = {'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize"))]})

        if (form.is_valid() and pendencies_form.is_valid()):
            return self.form_valid(form, pendencies_form)
        else:
            return self.form_invalid(form, pendencies_form)

    def get_initial(self):
        initial = super(PDFFileCreateView, self).get_initial()

        slug = self.kwargs.get('slug', '')

        topic = get_object_or_404(Topic, slug = slug)
        initial['subject'] = topic.subject

        return initial

    def form_invalid(self, form, pendencies_form):
        return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

    def form_valid(self, form, pendencies_form):
        self.object = form.save(commit = False)

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        self.object.topic = topic
        self.object.order = topic.resource_topic.count() + 1

        if not self.object.topic.visible and not self.object.topic.repository:
            self.object.visible = False

        self.object.save()

        pend_form = pendencies_form.save(commit = False)
        pend_form.resource = self.object

        if not pend_form.action == "":
            pend_form.save()

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['pdffile_id'] = self.object.id
        self.log_context['pdffile_name'] = self.object.name
        self.log_context['pdffile_slug'] = self.object.slug

        super(PDFFileCreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(PDFFileCreateView, self).get_context_data(**kwargs)

        context['title'] = _('Create PDF File')

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject
        context['mimeTypes'] = valid_formats

        return context

    def get_success_url(self):
        messages.success(self.request, _('The PDF File "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

        return reverse_lazy('subjects:topic_view', kwargs = {'slug': self.object.topic.subject.slug, 'topic_slug': self.object.topic.slug})


class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    log_component = 'resources'
    log_action = 'update'
    log_resource = 'pdffile'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'pdf_file/update.html'
    model = PDFFile
    form_class = PDFFileForm
    context_object_name = 'pdf_file'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        pend_form = self.object.pendencies_resource.all()

        if len(pend_form) > 0:
            pendencies_form = PendenciesForm(instance = pend_form[0], initial = {'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize"))]})
        else:
            pendencies_form = PendenciesForm(initial = {'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize"))]})

        return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        pend_form = self.object.pendencies_resource.all()

        if len(pend_form) > 0:
            pendencies_form = PendenciesForm(self.request.POST, instance = pend_form[0], initial = {'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize"))]})
        else:
            pendencies_form = PendenciesForm(self.request.POST, initial = {'subject': topic.subject.id, 'actions': [("", "-------"),("view", _("Visualize"))]})

        if (form.is_valid() and pendencies_form.is_valid()):
            return self.form_valid(form, pendencies_form)
        else:
            return self.form_invalid(form, pendencies_form)

    def form_invalid(self, form, pendencies_form):
        return self.render_to_response(self.get_context_data(form = form, pendencies_form = pendencies_form))

    def form_valid(self, form, pendencies_form):
        self.object = form.save(commit = False)

        if not self.object.topic.visible and not self.object.topic.repository:
            self.object.visible = False

        self.object.save()

        pend_form = pendencies_form.save(commit = False)
        pend_form.resource = self.object

        if not pend_form.action == "":
            pend_form.save()

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['pdffile_id'] = self.object.id
        self.log_context['pdffile_name'] = self.object.name
        self.log_context['pdffile_slug'] = self.object.slug

        super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        context['title'] = _('Update PDF File')

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject
        context['mimeTypes'] = valid_formats
        context['resource'] = get_object_or_404(PDFFile, slug = self.kwargs.get('slug', ''))

        return context

    def get_success_url(self):
        messages.success(self.request, _('The PDF File "%s" was updated successfully!')%(self.object.name))

        return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
    log_component = 'resources'
    log_action = 'delete'
    log_resource = 'pdf_file'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'resources/delete.html'
    model = PDFFile
    context_object_name = 'resource'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        pdf_file = get_object_or_404(PDFFile, slug = slug)

        if not has_subject_permissions(request.user, pdf_file.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, _('The PDF File "%s" was removed successfully from virtual environment "%s"!')%(self.object.name, self.object.topic.subject.name))

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['pdffile_id'] = self.object.id
        self.log_context['pdffile_name'] = self.object.name
        self.log_context['pdffile_slug'] = self.object.slug

        super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

class StatisticsView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view_statistics'
    log_resource = 'pdf_file'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = PDFFile
    template_name = 'pdf_file/relatorios.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        pdf_file = get_object_or_404(PDFFile, slug = slug)

        if not has_subject_permissions(request.user, pdf_file.topic.subject):
        	return redirect(reverse_lazy('subjects:home'))

        return super(StatisticsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatisticsView, self).get_context_data(**kwargs)

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['pdffile_id'] = self.object.id
        self.log_context['pdffile_name'] = self.object.name
        self.log_context['pdffile_slug'] = self.object.slug

        super(StatisticsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)


        context['title'] = _('PDF File Reports')

        slug = self.kwargs.get('slug')
        pdf_file = get_object_or_404(PDFFile, slug = slug)
        context['pdf_file'] = pdf_file
        date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language','') == 'pt-br' else "%m/%d/%Y %I:%M %p"
        if self.request.GET.get('language','') == "":
            start_date = datetime.datetime.now() - datetime.timedelta(30)
            end_date = datetime.datetime.now()
        else :
            start_date = datetime.datetime.strptime(self.request.GET.get('init_date',''),date_format)
            end_date = datetime.datetime.strptime(self.request.GET.get('end_date',''),date_format)

        context["init_date"] = start_date
        context["end_date"] = end_date
        alunos = pdf_file.students.all()
        if pdf_file.all_students :
        	alunos = pdf_file.topic.subject.students.all()

        vis_ou = Log.objects.filter(context__contains={'pdffile_id':pdf_file.id},resource="pdffile",action="view",user_email__in=(aluno.email for aluno in alunos), datetime__range=(start_date,end_date + datetime.timedelta(minutes = 1)))
        did,n_did,history = str(_("Realized")),str(_("Unrealized")),str(_("Historic"))
        re = []
        data_n_did,data_history = [],[]
        json_n_did, json_history = {},{}


        for log_al in vis_ou.order_by("datetime"):
            data_history.append([str(alunos.get(email=log_al.user_email)),
            ", ".join([str(x) for x in pdf_file.topic.subject.group_subject.filter(participants__email=log_al.user_email)]),
            log_al.action,log_al.datetime])
        
        json_history["data"] = data_history

        not_view = alunos.exclude(email__in=[log.user_email for log in vis_ou.distinct("user_email")])
        index = 0
        for alun in not_view:
            data_n_did.append([index,str(alun),", ".join([str(x) for x in pdf_file.topic.subject.group_subject.filter(participants__email=alun.email)]),str(_('View')), str(alun.email)])
            index += 1
        json_n_did["data"] = data_n_did


        context["json_n_did"] = json_n_did
        context["json_history"] = json_history
        c_visualizou = vis_ou.distinct("user_email").count()
        column_view = str(_('View'))
        re.append([str(_('PDF File')),did,n_did])
        re.append([column_view,c_visualizou, alunos.count() - c_visualizou])
        context['topic'] = pdf_file.topic
        context['subject'] = pdf_file.topic.subject
        context['db_data'] = re
        context['title_chart'] = _('Actions about resource')
        context['title_vAxis'] = _('Quantity')
        context['view'] = column_view
        context["n_did_table"] = n_did
        context["did_table"] = did
        context["history_table"] = history
        return context

from django.http import HttpResponse #used to send HTTP 404 error to ajax

class SendMessage(LoginRequiredMixin, LogMixin, generic.edit.FormView):
    log_component = 'resources'
    log_action = 'send'
    log_resource = 'pdffile'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'pdf_file/send_message.html'
    form_class = FormModalMessage

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        pdf_file = get_object_or_404(PDFFile, slug = slug)
        self.pdf_file = pdf_file
        
        if not has_subject_permissions(request.user, pdf_file.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SendMessage, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        message = form.cleaned_data.get('comment')
        image = form.cleaned_data.get("image")
        users = (self.request.POST.get('users[]','')).split(",")
        user = self.request.user
        subject = self.pdf_file.topic.subject

        if (users[0] is not ''):
            for u in users:
                to_user = User.objects.get(email=u)
                talk, create = Conversation.objects.get_or_create(user_one=user,user_two=to_user)
                created = TalkMessages.objects.create(text=message,talk=talk,user=user,subject=subject,image=image)
                
                simple_notify = textwrap.shorten(strip_tags(message), width = 30, placeholder = "...")

                if image is not '':
                    simple_notify += " ".join(_("[Photo]"))
                
                notification = {
                    "type": "chat",
                    "subtype": "subject",
                    "space": subject.slug,
                    "user_icon": created.user.image_url,
                    "notify_title": str(created.user),
                    "simple_notify": simple_notify,
                    "view_url": reverse("chat:view_message", args = (created.id, ), kwargs = {}),
                    "complete": render_to_string("chat/_message.html", {"talk_msg": created}, self.request),
                    "container": "chat-" + str(created.user.id),
                    "last_date": _("Last message in %s")%(formats.date_format(created.create_date, "SHORT_DATETIME_FORMAT"))
                }

                notification = json.dumps(notification)

                Group("user-%s" % to_user.id).send({'text': notification})

                ChatVisualizations.objects.create(viewed = False, message = created, user = to_user)
            
            success = str(_('The message was successfull sent!'))
            return JsonResponse({"message":success})
        erro = HttpResponse(str(_("No user selected!")))
        erro.status_code = 404
        return erro

    def get_context_data(self, **kwargs):
        context = super(SendMessage,self).get_context_data()
        context["pdf_file"] = get_object_or_404(PDFFile, slug=self.kwargs.get('slug', ''))
        return context

