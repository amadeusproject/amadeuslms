""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import datetime
import json
import textwrap

from asgiref.sync import async_to_sync
from braces import views as braces_mixins
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse  # used to send HTTP 404 error to ajax
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import formats
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from amadeus.permissions import has_subject_permissions, has_resource_permissions
from chat.models import Conversation, TalkMessages, ChatVisualizations
from log.models import Log
from topics.models import Topic
from users.models import User
from webpage.forms import FormModalMessage
from .forms import WebconferenceForm, SettingsForm, InlinePendenciesFormset, WebConferenceUpdateForm
from .models import Webconference, ConferenceSettings as Settings, ViewWebConferenceLog, \
    InitWebConferenceLog, CreateWebConferenceLog, DeleteWebConferenceLog, \
    ViewStatisticsConferenceLog, SendMessageInWebConferenceLog, UpdateWebConferenceLog, \
    InsideViewWebConferenceLog, ParticipatingInWebConferenceLog, EndParticipationInConferenceLog


class NewWindowView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'webconference/window_view.html'
    model = Webconference
    context_object_name = 'webconference'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        webconference = get_object_or_404(Webconference, slug=slug)

        if not has_resource_permissions(request.user, webconference):
            return redirect(reverse_lazy('subjects:home'))

        return super(NewWindowView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NewWindowView, self).get_context_data(**kwargs)
        context['title'] = _("%s - Web Conference") % (self.object.name)
        view_log = ViewWebConferenceLog(user=self.request.user, subject=self.object.topic.subject,
                                        category=self.object.topic.subject.category,
                                        webconference=self.object, topic=self.object.topic)
        view_log.save()

        self.request.session['log_id'] = Log.objects.latest('id').id

        return context


class Conference(LoginRequiredMixin, generic.TemplateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'webconference/jitsi.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        conference = get_object_or_404(Webconference, slug=slug)

        if not has_resource_permissions(request.user, conference):
            return redirect(reverse_lazy('subjects:home'))

        return super(Conference, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        window = self.kwargs.get('window', None)

        template_name = 'webconference/jitsi.html'

        if window:
            template_name = 'webconference/window_jitsi.html'

        return template_name

    def get_context_data(self, **kwargs):
        context = super(Conference, self).get_context_data(**kwargs)
        conference = get_object_or_404(Webconference, slug=kwargs.get('slug'))
        context['title'] = _("%s - Web Conference") % (conference)
        context['webconference'] = conference
        context['topic'] = conference.topic
        context['subject'] = conference.topic.subject
        context['name_room'] = kwargs.get('slug')

        context['user_image'] = self.request.build_absolute_uri(str(self.request.user.image_url))

        init_log = InitWebConferenceLog(user=self.request.user, subject=self.object.topic.subject,
                                        category=self.object.topic.subject.category,
                                        webconference=self.object, topic=self.object.topic)
        init_log.save()

        try:
            context['domain'] = Settings.objects.last().domain
        except AttributeError:
            context['domain'] = 'meet.jit.si'

        return context


def participating(request):
    webconference = get_object_or_404(Webconference, slug=request.GET['slug'])
    participating_log = ParticipatingInWebConferenceLog(
        user=request.user, subject=webconference.topic.subject,
        category=webconference.topic.subject.category, webconference=webconference,
        topic=webconference.topic)
    participating_log.save()

    return JsonResponse({'message': 'ok'})


def finish(request):
    webconference = get_object_or_404(Webconference, slug=request.GET['roomName'])

    end_participation_log = EndParticipationInConferenceLog(
        user=request.user,
        subject=webconference.topic.subject,
        category=webconference.topic.subject.category,
        webconference=webconference,
        topic=webconference.topic)
    end_participation_log.save()
    url = {
        'url': str(reverse_lazy('webconferences:view', kwargs={'slug': request.GET['roomName']}))}
    return JsonResponse(url, safe=False)


class InsideView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'webconference/view.html'
    model = Webconference
    context_object_name = 'webconference'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        webconference = get_object_or_404(Webconference, slug=slug)

        if not has_resource_permissions(request.user, webconference):
            return redirect(reverse_lazy('subjects:home'))

        return super(InsideView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InsideView, self).get_context_data(**kwargs)

        context['title'] = self.object.name

        context['topic'] = self.object.topic
        context['subject'] = self.object.topic.subject

        inside_view_log = InsideViewWebConferenceLog(user=self.request.user,
                                                     subject=self.object.topic.subject,
                                                     category=self.object.topic.subject.category,
                                                     webconference=self.object,
                                                     topic=self.object.topic)
        inside_view_log.save()

        self.request.session['log_id'] = Log.objects.latest('id').id

        return context


class CreateView(LoginRequiredMixin, generic.edit.CreateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'webconference/create.html'
    form_class = WebconferenceForm

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy('subjects:home'))
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)
        pendencies_form = InlinePendenciesFormset(initial=[{'subject': topic.subject.id,
                                                            'actions': [("", "-------"),
                                                                        ("view", _("Visualize")), (
                                                                            "participate",
                                                                            _("Participate"))]}])

        return self.render_to_response(
            self.get_context_data(form=form, pendencies_form=pendencies_form))

    def post(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        pendencies_form = InlinePendenciesFormset(self.request.POST, initial=[
            {'subject': topic.subject.id, 'actions': [("", "-------"), ("view", _("Visualize")),
                                                      ("participate", _("Participate"))]}])

        if form.is_valid() and pendencies_form.is_valid():
            return self.form_valid(form, pendencies_form)
        else:
            return self.form_invalid(form, pendencies_form)

    def get_initial(self):
        initial = super(CreateView, self).get_initial()

        slug = self.kwargs.get('slug', '')

        topic = get_object_or_404(Topic, slug=slug)
        initial['subject'] = topic.subject

        return initial

    def form_invalid(self, form, pendencies_form):
        for p_form in pendencies_form.forms:
            p_form.fields['action'].choices = [("", "-------"), ("view", _("Visualize")),
                                               ("participate", _("Participate"))]
        return self.render_to_response(
            self.get_context_data(form=form, pendencies_form=pendencies_form))

    def form_valid(self, form, pendencies_form):

        self.object = form.save(commit=False)
        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        self.object.topic = topic
        self.object.order = topic.resource_topic.count() + 1

        if not self.object.topic.visible and not self.object.topic.repository:
            self.object.visible = False

        self.object.save()
        pendencies_form.instance = self.object
        pendencies_form.save(commit=False)

        for pform in pendencies_form.forms:
            pend_form = pform.save(commit=False)

            if not pend_form.action == "":
                pend_form.save()

        create_log = CreateWebConferenceLog(user=self.request.user,
                                            subject=self.object.topic.subject,
                                            category=self.object.topic.subject.category,
                                            webconference=self.object, topic=self.object.topic)
        create_log.save()

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)

        context['title'] = _('Create Web Conference')

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        context['topic'] = topic
        context['subject'] = topic.subject

        return context

    def get_success_url(self):
        messages.success(self.request, _(
            'The Web conference "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!') % (
                             self.object.name, self.object.topic.name,
                             self.object.topic.subject.name))

        success_url = reverse_lazy('webconferences:view', kwargs={'slug': self.object.slug})

        if self.object.show_window:
            self.request.session['resources'] = {}
            self.request.session['resources']['new_page'] = True
            self.request.session['resources']['new_page_url'] = reverse(
                'webconferences:window_view', kwargs={'slug': self.object.slug})

            success_url = reverse_lazy('subjects:view',
                                       kwargs={'slug': self.object.topic.subject.slug})

        return success_url


class UpdateView(LoginRequiredMixin, generic.UpdateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'webconference/update.html'
    model = Webconference
    form_class = WebConferenceUpdateForm

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        pendencies_form = InlinePendenciesFormset(instance=self.object, initial=[
            {'subject': topic.subject.id, 'actions': [("", "-------"), ("view", _("Visualize")),
                                                      ("participate", _("Participate"))]}])

        return self.render_to_response(
            self.get_context_data(form=form, pendencies_form=pendencies_form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        pendencies_form = InlinePendenciesFormset(self.request.POST, instance=self.object, initial=[
            {'subject': topic.subject.id, 'actions': [("", "-------"), ("view", _("Visualize")),
                                                      ("participate", _("Participate"))]}])

        if form.is_valid() and pendencies_form.is_valid():
            return self.form_valid(form, pendencies_form)
        else:
            return self.form_invalid(form, pendencies_form)

    def form_invalid(self, form, pendencies_form):
        for p_form in pendencies_form.forms:
            p_form.fields['action'].choices = [("", "-------"), ("view", _("Visualize")),
                                               ("participate", _("Participate"))]

        return self.render_to_response(
            self.get_context_data(form=form, pendencies_form=pendencies_form))

    def form_valid(self, form, pendencies_form):
        self.object = form.save(commit=False)

        if not self.object.topic.visible and not self.object.topic.repository:
            self.object.visible = False

        self.object.save()

        pendencies_form.instance = self.object
        pendencies_form.save(commit=False)

        for form in pendencies_form.forms:
            pend_form = form.save(commit=False)

            if not pend_form.action == "":
                pend_form.save()

        update_log = UpdateWebConferenceLog(user=self.request.user,
                                            subject=self.object.topic.subject,
                                            category=self.object.topic.subject.category,
                                            webconference=self.object, topic=self.object.topic)
        update_log.save()

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        context['title'] = _('Update Web Conference')

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        context['topic'] = topic
        context['subject'] = topic.subject
        context['resource'] = get_object_or_404(Webconference, slug=self.kwargs.get('slug', ''))

        return context

    def get_success_url(self):
        messages.success(self.request, _('The Web conference "%s" was updated successfully!') % (
            self.object.name))

        success_url = reverse_lazy('webconferences:view', kwargs={'slug': self.object.slug})

        if self.object.show_window:
            self.request.session['resources'] = {}
            self.request.session['resources']['new_page'] = True
            self.request.session['resources']['new_page_url'] = reverse(
                'webconferences:window_view', kwargs={'slug': self.object.slug})

            success_url = reverse_lazy('subjects:view',
                                       kwargs={'slug': self.object.topic.subject.slug})

        return success_url


class DeleteView(LoginRequiredMixin, generic.DeleteView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'resources/delete.html'
    model = Webconference
    context_object_name = 'resource'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        webconference = get_object_or_404(Webconference, slug=slug)

        if not has_subject_permissions(request.user, webconference.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, _(
            'The web conference "%s" was removed successfully from virtual environment "%s"!') % (
                             self.object.name, self.object.topic.subject.name))

        delete_log = DeleteWebConferenceLog(user=self.request.user,
                                            subject=self.object.topic.subject,
                                            category=self.object.topic.subject.category,
                                            webconference=self.object, topic=self.object.topic)
        delete_log.save()

        return reverse_lazy('subjects:view', kwargs={'slug': self.object.topic.subject.slug})


class ConferenceSettings(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin,
                         generic.UpdateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'webconference/config.html'
    model = Settings
    form_class = SettingsForm
    success_url = reverse_lazy("subjects:home")

    def get_object(self, queryset=None):
        return Settings.objects.last()

    def form_valid(self, form):
        form.save()

        messages.success(self.request, _("Conference settings updated successfully!"))

        return super(ConferenceSettings, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ConferenceSettings, self).get_context_data(**kwargs)

        context['title'] = _('Web Conference Settings')

        return context


class StatisticsView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Webconference
    template_name = 'webconference/relatorios.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        webconference = get_object_or_404(Webconference, slug=slug)

        if not has_subject_permissions(request.user, webconference.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(StatisticsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatisticsView, self).get_context_data(**kwargs)

        view_statistics_log = ViewStatisticsConferenceLog(user=self.request.user,
                                                          subject=self.object.topic.subject,
                                                          category=self.object.topic.subject.category,
                                                          webconference=self.object,
                                                          topic=self.object.topic)
        view_statistics_log.save()
        context['title'] = _('Youtube Video Reports')

        slug = self.kwargs.get('slug')
        webconference = get_object_or_404(Webconference, slug=slug)

        date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language',
                                                               '') == 'pt-br' else "%m/%d/%Y %I:%M %p"
        if self.request.GET.get('language', '') == "":
            start_date = datetime.datetime.now() - datetime.timedelta(30)
            end_date = datetime.datetime.now()
        else:
            start_date = datetime.datetime.strptime(self.request.GET.get('init_date', ''),
                                                    date_format)
            end_date = datetime.datetime.strptime(self.request.GET.get('end_date', ''), date_format)
        context["init_date"] = start_date
        context["end_date"] = end_date
        alunos = webconference.students.all()
        if webconference.all_students:
            alunos = webconference.topic.subject.students.all()

        vis_ou = Log.objects.filter(context__contains={'webconference_id': webconference.id},
                                    resource="webconference",
                                    user_email__in=(aluno.email for aluno in alunos),
                                    datetime__range=(
                                        start_date,
                                        end_date + datetime.timedelta(minutes=1))).filter(
            Q(action="view") | Q(action="initwebconference") | Q(action="participating"))
        did, n_did, history = str(_("Realized")), str(_("Unrealized")), str(_("Historic"))
        re = []
        data_n_did, data_history = [], []
        json_n_did, json_history = {}, {}

        for log_al in vis_ou.order_by("datetime"):
            data_history.append([str(alunos.get(email=log_al.user_email)),
                                 ", ".join([str(x) for x in
                                            webconference.topic.subject.group_subject.filter(
                                                participants__email=log_al.user_email)]),
                                 log_al.action, log_al.datetime])

        json_history["data"] = data_history

        column_view, column_initwebconference, column_participate = str(_('View')), str(
            _('Enter')), str(_('Participate'))

        not_view = alunos.exclude(email__in=[log.user_email for log in
                                             vis_ou.filter(action="view").distinct("user_email")])
        index = 0
        for alun in not_view:
            data_n_did.append([index, str(alun), ", ".join([str(x) for x in
                                                            webconference.topic.subject.group_subject.filter(
                                                                participants__email=alun.email)]),
                               column_view, str(alun.email)])
            index += 1

        not_initwebconference = alunos.exclude(email__in=[log.user_email for log in vis_ou.filter(
            action="initwebconference").distinct("user_email")])
        for alun in not_initwebconference:
            data_n_did.append([index, str(alun), ", ".join([str(x) for x in
                                                            webconference.topic.subject.group_subject.filter(
                                                                participants__email=alun.email)]),
                               column_initwebconference, str(alun.email)])
            index += 1

        not_participate = alunos.exclude(email__in=[log.user_email for log in
                                                    vis_ou.filter(action="participating").distinct(
                                                        "user_email")])
        for alun in not_participate:
            data_n_did.append([index, str(alun), ", ".join([str(x) for x in
                                                            webconference.topic.subject.group_subject.filter(
                                                                participants__email=alun.email)]),
                               column_participate, str(alun.email)])
            index += 1

        json_n_did["data"] = data_n_did

        context["json_n_did"] = json_n_did
        context["json_history"] = json_history
        c_visualizou = vis_ou.filter(action="view").distinct("user_email").count()
        c_initwebconference = vis_ou.filter(action="initwebconference").distinct(
            "user_email").count()
        c_participate = vis_ou.filter(action="participating").distinct("user_email").count()
        re.append([str(_('Webconference')), did, n_did])

        re.append([column_view, c_visualizou, alunos.count() - c_visualizou])
        re.append(
            [column_initwebconference, c_initwebconference, alunos.count() - c_initwebconference])
        re.append([column_participate, c_participate, alunos.count() - c_participate])

        context['view'] = column_view
        context['initwebconference'] = column_initwebconference
        context['participate'] = column_participate
        context['topic'] = webconference.topic
        context['subject'] = webconference.topic.subject
        context['webconference'] = webconference
        context['db_data'] = re
        context['title_chart'] = _('Actions about resource')
        context['title_vAxis'] = _('Quantity')

        context["n_did_table"] = n_did
        context["did_table"] = did
        context["history_table"] = history
        return context


class SendMessage(LoginRequiredMixin, generic.edit.FormView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'webconference/send_message.html'
    form_class = FormModalMessage

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        webconference = get_object_or_404(Webconference, slug=slug)
        self.webconference = webconference

        if not has_subject_permissions(request.user, webconference.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SendMessage, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        message = form.cleaned_data.get('comment')
        image = form.cleaned_data.get("image")
        users = (self.request.POST.get('users[]', '')).split(",")
        user = self.request.user
        subject = self.webconference.topic.subject

        channel_layer = get_channel_layer()

        send_message_in_chat_log = SendMessageInWebConferenceLog(
            user=self.request.user,
            subject=self.webconference.topic.subject,
            category=self.webconference.topic.subject.category,
            webconference=self.webconference,
            topic=self.webconference.topic,
            message=message)
        send_message_in_chat_log.save()

        if users[0] is not '':
            for u in users:
                to_user = User.objects.get(email=u)
                talk, create = Conversation.objects.get_or_create(user_one=user, user_two=to_user)
                created = TalkMessages.objects.create(text=message, talk=talk, user=user,
                                                      subject=subject, image=image)

                simple_notify = textwrap.shorten(strip_tags(message), width=30, placeholder="...")

                if image is not '':
                    simple_notify += " ".join(_("[Photo]"))

                notification = {
                    "type": "chat",
                    "subtype": "subject",
                    "space": subject.slug,
                    "user_icon": created.user.image_url,
                    "notify_title": str(created.user),
                    "simple_notify": simple_notify,
                    "view_url": reverse("chat:view_message", args=(created.id,), kwargs={}),
                    "complete": render_to_string("chat/_message.html", {"talk_msg": created},
                                                 self.request),
                    "container": "chat-" + str(created.user.id),
                    "last_date": _("Last message in %s") % (
                        formats.date_format(created.create_date, "SHORT_DATETIME_FORMAT"))
                }

                notification = json.dumps(notification)
                async_to_sync(channel_layer.send)("user-%s" % to_user.id, {'text': notification})

                ChatVisualizations.objects.create(viewed=False, message=created, user=to_user)

            success = str(_('The message was successfull sent!'))
            return JsonResponse({"message": success})
        erro = HttpResponse(str(_("No user selected!")))
        erro.status_code = 404
        return erro

    def get_context_data(self, **kwargs):
        context = super(SendMessage, self).get_context_data()
        context["webconference"] = get_object_or_404(Webconference,
                                                     slug=self.kwargs.get('slug', ''))
        return context
