""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Link
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import LinkForm
from rolepermissions.mixins import HasRoleMixin

from log.mixins import LogMixin
from log.decorators import log_decorator_ajax
from log.models import Log

from django.contrib import messages
from pendencies.forms import PendenciesForm

from amadeus.permissions import has_subject_permissions, has_resource_permissions

from topics.models import Topic

import datetime
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

# Create your views here.
class CreateLinkView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
    log_component = 'resources'
    log_action = 'create'
    log_resource = 'link'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'links/create.html'
    form_class = LinkForm

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(CreateLinkView, self).dispatch(request, *args, **kwargs)

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
        initial = super(CreateLinkView, self).get_initial()

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

        self.object.show_window = True

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
        self.log_context['link_id'] = self.object.id
        self.log_context['link_name'] = self.object.name
        self.log_context['link_slug'] = self.object.slug

        super(CreateLinkView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateLinkView, self).get_context_data(**kwargs)

        context['title'] = _('Create Webiste Link')

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject

        return context

    def get_success_url(self):
        messages.success(self.request, _('The  Link "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

        return reverse_lazy('subjects:topic_view', kwargs = {'slug': self.object.topic.subject.slug, 'topic_slug': self.object.topic.slug})
        



class DeleteLinkView(LoginRequiredMixin, LogMixin, generic.edit.DeleteView):


    log_component = 'resources'
    log_action = 'delete'
    log_resource = 'link'
    log_context = {}
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Link
    template_name = 'links/delete.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        link = get_object_or_404(Link, slug = slug)

        if not has_subject_permissions(request.user, link.topic.subject):
            return redirect(reverse_lazy('subjects:home'))
        return super(DeleteLinkView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, _('The Website Link "%s" was removed successfully from virtual environment "%s"!')%(self.object.name, self.object.topic.subject.name))

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['link_id'] = self.object.id
        self.log_context['link_name'] = self.object.name
        self.log_context['link_slug'] = self.object.slug
       
        super(DeleteLinkView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

from django.views.generic.base import RedirectView

class RedirectUrl(LogMixin, RedirectView):
    log_component = 'resources'
    log_action = 'view'
    log_resource = 'link'
    log_context = {}

    def get_redirect_url(self, *args, **kwargs):
        link = get_object_or_404(Link,slug=self.kwargs.get("slug",""))
        self.log_context['category_id'] = link.topic.subject.category.id
        self.log_context['category_name'] = link.topic.subject.category.name
        self.log_context['category_slug'] = link.topic.subject.category.slug
        self.log_context['subject_id'] = link.topic.subject.id
        self.log_context['subject_name'] = link.topic.subject.name
        self.log_context['subject_slug'] = link.topic.subject.slug
        self.log_context['topic_id'] = link.topic.id
        self.log_context['topic_name'] = link.topic.name
        self.log_context['topic_slug'] = link.topic.slug
        self.log_context['link_id'] = link.id
        self.log_context['link_name'] = link.name
        self.log_context['link_slug'] = link.slug

        super(RedirectUrl, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return link.link_url

class UpdateLinkView(LoginRequiredMixin, LogMixin, generic.edit.UpdateView):
    
    log_component = 'resources'
    log_action = 'update'
    log_resource = 'links'
    log_context = {}
    model = Link
    form_class = LinkForm
    template_name = 'links/update.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):


        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(UpdateLinkView, self).dispatch(request, *args, **kwargs)


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

        self.object.show_window = True
        
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
        self.log_context['link_id'] = self.object.id
        self.log_context['link_name'] = self.object.name
        self.log_context['link_slug'] = self.object.slug

        super(UpdateLinkView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateLinkView, self).get_context_data(**kwargs)

        context['title'] = _('Update Website Link')

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject
        context['resource'] = get_object_or_404(Link, slug = self.kwargs.get('slug', ''))

        return context

    def get_success_url(self):
        messages.success(self.request, _('The Website Link "%s" was updated successfully!')%(self.object.name))

        return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})


class StatisticsView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view_statistics'
    log_resource = 'link'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Link
    template_name = 'links/relatorios.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        link = get_object_or_404(Link, slug = slug)

        if not has_subject_permissions(request.user, link.topic.subject):
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
        self.log_context['link_id'] = self.object.id
        self.log_context['link_name'] = self.object.name
        self.log_context['link_slug'] = self.object.slug

        super(StatisticsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)


        context['title'] = _('Links Reports')

        slug = self.kwargs.get('slug')
        link = get_object_or_404(Link, slug = slug)

        date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language','') == 'pt-br' else "%m/%d/%Y %I:%M %p"
        if self.request.GET.get('language','') == "":
            start_date = datetime.datetime.now() - datetime.timedelta(30)
            end_date = datetime.datetime.now()
        else :
            start_date = datetime.datetime.strptime(self.request.GET.get('init_date',''),date_format)
            end_date = datetime.datetime.strptime(self.request.GET.get('end_date',''),date_format)
        context["init_date"] = start_date
        context["end_date"] = end_date
        alunos = link.students.all()
        if link.all_students :
        	alunos = link.topic.subject.students.all()

        vis_ou = Log.objects.filter(context__contains={'link_id':link.id},resource="link",action="view",user_email__in=(aluno.email for aluno in alunos), datetime__range=(start_date,end_date + datetime.timedelta(minutes = 1)))
        did,n_did,history = str(_("Realized")),str(_("Unrealized")),str(_("Historic"))
        re = []
        data_n_did,data_history = [],[]
        json_n_did, json_history = {},{}

        for log_al in vis_ou.order_by("datetime"):
            data_history.append([str(alunos.get(email=log_al.user_email)),
            ", ".join([str(x) for x in link.topic.subject.group_subject.filter(participants__email=log_al.user_email)]),
            log_al.action,log_al.datetime])
        
        json_history["data"] = data_history

        not_view = alunos.exclude(email__in=[log.user_email for log in vis_ou.distinct("user_email")])
        index = 0
        for alun in not_view:
            data_n_did.append([index,str(alun),", ".join([str(x) for x in link.topic.subject.group_subject.filter(participants__email=alun.email)]),str(_('View')), str(alun.email)])
            index += 1
        json_n_did["data"] = data_n_did


        context["json_n_did"] = json_n_did
        context["json_history"] = json_history
        c_visualizou = vis_ou.distinct("user_email").count()
        column_view = str(_('View'))
        re.append([str(_('Links')),did,n_did])
        re.append([column_view,c_visualizou, alunos.count() - c_visualizou])
        context['topic'] = link.topic
        context['subject'] = link.topic.subject
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
    log_resource = 'link'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'links/send_message.html'
    form_class = FormModalMessage

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        link = get_object_or_404(Link, slug = slug)
        self.link = link
        
        if not has_subject_permissions(request.user, link.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SendMessage, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        message = form.cleaned_data.get('comment')
        image = form.cleaned_data.get("image")
        users = (self.request.POST.get('users[]','')).split(",")
        user = self.request.user
        subject = self.link.topic.subject

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
        context["link"] = get_object_or_404(Link, slug=self.kwargs.get('slug', ''))
        return context
    
