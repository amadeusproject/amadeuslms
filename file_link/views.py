""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, Http404
from os import path
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from amadeus.permissions import has_subject_permissions, has_resource_permissions

from log.mixins import LogMixin

from topics.models import Topic

from pendencies.forms import PendenciesForm

from .forms import FileLinkForm
from .models import FileLink, valid_formats


import datetime
from log.models import Log
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

class DownloadFile(LoginRequiredMixin, LogMixin, generic.DetailView):
	log_component = 'resources'
	log_action = 'view'
	log_resource = 'filelink'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	model = FileLink

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		file_link = get_object_or_404(FileLink, slug = slug)

		if not has_resource_permissions(request.user, file_link):
			return redirect(reverse_lazy('subjects:home'))

		return super(DownloadFile, self).dispatch(request, *args, **kwargs)

	def render_to_response(self, context, **response_kwargs):
		slug = self.kwargs.get('slug', '')
		file_link = get_object_or_404(FileLink, slug = slug)

		if not path.exists(file_link.file_content.path):
			raise Http404()

		response = HttpResponse(open(file_link.file_content.path, 'rb').read())
		response['Content-Type'] = 'application/force-download'
		response['Pragma'] = 'public'
		response['Expires'] = '0'
		response['Cache-Control'] = 'must-revalidate, post-check=0, pre-check=0'
		response['Content-Disposition'] = 'attachment; filename=%s' % file_link.filename
		response['Content-Transfer-Encoding'] = 'binary'
		response['Content-Length'] = str(path.getsize(file_link.file_content.path))

		self.log_context['category_id'] = file_link.topic.subject.category.id
		self.log_context['category_name'] = file_link.topic.subject.category.name
		self.log_context['category_slug'] = file_link.topic.subject.category.slug
		self.log_context['subject_id'] = file_link.topic.subject.id
		self.log_context['subject_name'] = file_link.topic.subject.name
		self.log_context['subject_slug'] = file_link.topic.subject.slug
		self.log_context['topic_id'] = file_link.topic.id
		self.log_context['topic_name'] = file_link.topic.name
		self.log_context['topic_slug'] = file_link.topic.slug
		self.log_context['filelink_id'] = file_link.id
		self.log_context['filelink_name'] = file_link.name
		self.log_context['filelink_slug'] = file_link.slug

		super(DownloadFile, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context) 
		
		return response

class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = 'resources'
	log_action = 'create'
	log_resource = 'filelink'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'file_links/create.html'
	form_class = FileLinkForm

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		if not has_subject_permissions(request.user, topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(CreateView, self).dispatch(request, *args, **kwargs)

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
		initial = super(CreateView, self).get_initial()

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
		self.log_context['filelink_id'] = self.object.id
		self.log_context['filelink_name'] = self.object.name
		self.log_context['filelink_slug'] = self.object.slug

		super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)

		context['title'] = _('Create File Link')

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject
		context['mimeTypes'] = valid_formats

		return context

	def get_success_url(self):
		messages.success(self.request, _('The File Link "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
	log_component = 'resources'
	log_action = 'update'
	log_resource = 'filelink'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'file_links/update.html'
	model = FileLink
	form_class = FileLinkForm
	context_object_name = 'file_link'

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
		self.log_context['filelink_id'] = self.object.id
		self.log_context['filelink_name'] = self.object.name
		self.log_context['filelink_slug'] = self.object.slug

		super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)

		context['title'] = _('Update File Link')

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject
		context['mimeTypes'] = valid_formats
		context['resource'] = get_object_or_404(FileLink, slug = self.kwargs.get('slug', ''))

		return context

	def get_success_url(self):
		messages.success(self.request, _('The File Link "%s" was updated successfully!')%(self.object.name))

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = 'resources'
	log_action = 'delete'
	log_resource = 'filelink'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'resources/delete.html'
	model = FileLink
	context_object_name = 'resource'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		file_link = get_object_or_404(FileLink, slug = slug)

		if not has_subject_permissions(request.user, file_link.topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(DeleteView, self).dispatch(request, *args, **kwargs)

	def get_success_url(self):
		messages.success(self.request, _('The File Link "%s" was removed successfully from virtual environment "%s"!')%(self.object.name, self.object.topic.subject.name))

		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['filelink_id'] = self.object.id
		self.log_context['filelink_name'] = self.object.name
		self.log_context['filelink_slug'] = self.object.slug

		super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})


class StatisticsView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view_statistics'
    log_resource = 'filelink'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = FileLink
    template_name = 'file_links/relatorios.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        filelink = get_object_or_404(FileLink, slug = slug)

        if not has_subject_permissions(request.user, filelink.topic.subject):
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
        self.log_context['filelink_id'] = self.object.id
        self.log_context['filelink_name'] = self.object.name
        self.log_context['filelink_slug'] = self.object.slug

        super(StatisticsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)


        context['title'] = _('File Link Reports')

        slug = self.kwargs.get('slug')
        filelink = get_object_or_404(FileLink, slug = slug)

        date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language','') == 'pt-br' else "%m/%d/%Y %I:%M %p"
        if self.request.GET.get('language','') == "":
            start_date = datetime.datetime.now() - datetime.timedelta(30)
            end_date = datetime.datetime.now()
        else :
            start_date = datetime.datetime.strptime(self.request.GET.get('init_date',''),date_format)
            end_date = datetime.datetime.strptime(self.request.GET.get('end_date',''),date_format)
        context["init_date"] = start_date
        context["end_date"] = end_date
        alunos = filelink.students.all()
        if filelink.all_students :
        	alunos = filelink.topic.subject.students.all()

        vis_ou = Log.objects.filter(context__contains={'filelink_id':filelink.id},resource="filelink",action="view",user_email__in=(aluno.email for aluno in alunos), datetime__range=(start_date,end_date + datetime.timedelta(minutes = 1)))
        did,n_did,history = str(_("Realized")),str(_("Unrealized")),str(_("Historic"))
        re = []
        data_n_did,data_history = [],[]
        json_n_did, json_history = {},{}

        for log_al in vis_ou.order_by("datetime"):
            data_history.append([str(alunos.get(email=log_al.user_email)),
            ", ".join([str(x) for x in filelink.topic.subject.group_subject.filter(participants__email=log_al.user_email)]),
            log_al.action,log_al.datetime])
        
        json_history["data"] = data_history

        not_view = alunos.exclude(email__in=[log.user_email for log in vis_ou.distinct("user_email")])
        index = 0
        for alun in not_view:
            data_n_did.append([index,str(alun),", ".join([str(x) for x in filelink.topic.subject.group_subject.filter(participants__email=alun.email)]),str(_('View')), str(alun.email)])
            index += 1
        json_n_did["data"] = data_n_did


        context["json_n_did"] = json_n_did
        context["json_history"] = json_history
        c_visualizou = vis_ou.distinct("user_email").count()
        column_view = str(_('View'))
        re.append([str(_('File link')),did,n_did])
        re.append([column_view,c_visualizou, alunos.count() - c_visualizou])
        context['topic'] = filelink.topic
        context['subject'] = filelink.topic.subject
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
    log_resource = 'filelink'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'file_links/send_message.html'
    form_class = FormModalMessage

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        filelink = get_object_or_404(FileLink, slug = slug)
        self.filelink = filelink
        
        if not has_subject_permissions(request.user, filelink.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SendMessage, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        message = form.cleaned_data.get('comment')
        image = form.cleaned_data.get("image")
        users = (self.request.POST.get('users[]','')).split(",")
        user = self.request.user
        subject = self.filelink.topic.subject
        
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
        context["filelink"] = get_object_or_404(FileLink, slug=self.kwargs.get('slug', ''))
        return context
    
