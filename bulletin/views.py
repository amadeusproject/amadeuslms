from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from amadeus.permissions import has_subject_permissions, has_resource_permissions
from .utils import brodcast_dificulties
from goals.models import Goals,GoalItem

import xlwt
import time
import datetime
from log.mixins import LogMixin

from topics.models import Topic

from django.conf import settings
import os
from os.path import join

from pendencies.forms import PendenciesForm

from .forms import BulletinForm
from .models import Bulletin

from log.models import Log
from chat.models import Conversation, TalkMessages, ChatVisualizations
from users.models import User
from subjects.models import Subject

from .forms import FormModalMessage

from django.template.loader import render_to_string
from django.utils import formats
import textwrap
from django.utils.html import strip_tags
import json
from channels import Group

class NewWindowView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/window_view.html'
    model = Bulletin
    context_object_name = 'bulletin'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug=slug)

        if not has_resource_permissions(request.user, bulletin):
            return redirect(reverse_lazy('subjects:home'))

        return super(NewWindowView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NewWindowView, self).get_context_data(**kwargs)

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug
        self.log_context['timestamp_start'] = str(int(time.time()))

        super(NewWindowView, self).createLog(self.request.user, self.log_component, self.log_action,
                                             self.log_resource, self.log_context)

        self.request.session['log_id'] = Log.objects.latest('id').id

        return context

class InsideView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/view.html'
    model = Bulletin
    context_object_name = 'bulletin'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug=slug)

        if not has_resource_permissions(request.user, bulletin):
            return redirect(reverse_lazy('subjects:home'))

        return super(InsideView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        difficulties = self.request.POST.get('difficulties', None)

        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug=slug)

        self.object = bulletin

        if not difficulties is None and not difficulties == "":
            message = _("#Dificulty(ies) found in %s")%(str(bulletin)) + ":<p>" + difficulties + "</p>"

            brodcast_dificulties(self.request, message, bulletin.topic.subject)

            messages.success(self.request, message = _("Difficulties sent to the subject professor(s)"))
            return self.render_to_response(context = self.get_context_data())
        else:
            messages.error(self.request, message = _("You should inform some difficulty"))
            return self.render_to_response(context = self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(InsideView, self).get_context_data(**kwargs)

        context['title'] = self.object.name

        context['topic'] = self.object.topic
        context['subject'] = self.object.topic.subject

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug
        self.log_context['timestamp_start'] = str(int(time.time()))

        super(InsideView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        self.request.session['log_id'] = Log.objects.latest('id').id

        return context

class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
    log_component = 'resources'
    log_action = 'create'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/create.html'
    form_class = BulletinForm

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        existe_meta = Goals.objects.filter(topic=topic).exists()
        existe_boletim = Bulletin.objects.filter(topic=topic).exists()

        if not existe_meta:
            messages.error(request,_("The topic %s has no goals, so you can't create a Bulletin.") %(topic) )
            caminho1 = request.META['HTTP_REFERER']
            return redirect(caminho1)

        if existe_boletim:
            messages.error(request,_("The topic %s already has a Bulletin, so you can't create another.") %(topic) )
            caminho2 = request.META['HTTP_REFERER']
            return redirect(caminho2)

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
        self.object.all_students = True

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
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug

        super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)

        context['title'] = _('Create Bulletin')

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject


        meta_geral = Goals.objects.get(topic=topic)
        metas = GoalItem.objects.filter(goal = meta_geral)
        itens_da_meta = list(metas)
        alunos = meta_geral.topic.subject.students.all()
        create_excel_file(alunos, itens_da_meta,meta_geral)


        return context

    def get_success_url(self):
        messages.success(self.request, _('The Bulletin "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

        success_url = reverse_lazy('bulletin:view', kwargs = {'slug': self.object.slug})

        if self.object.show_window:
            self.request.session['resources'] = {}
            self.request.session['resources']['new_page'] = True
            self.request.session['resources']['new_page_url'] = reverse('bulletin:window_view', kwargs = {'slug': self.object.slug})

            success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

        return success_url

def create_excel_file(estudantes,metas,meta):
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u'Bulletin')
    worksheet.write(0, 0, u'ID do Usuário')
    worksheet.write(0, 1, u'Usuário')
    count_meta = 2
    contador_estudante = 1

    for m in metas:
        worksheet.write(0,count_meta,u'%s' % (m.description) )
        count_meta += 1
    for estudante in estudantes:
        worksheet.write(contador_estudante,0,estudante.id )
        if estudante.social_name:
            worksheet.write(contador_estudante,1,estudante.social_name)
        else:
            nome = estudante.username + " " + estudante.last_name
            worksheet.write(contador_estudante,1,nome)

        contador_estudante += 1

    folder_path = join(settings.BASE_DIR, 'bulletin\\localfiles')
    #check if the folder already exists
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    workbook.save(settings.BASE_DIR+"\\bulletin\\localfiles\\"+str(meta.slug)+".xls")



class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    log_component = 'resources'
    log_action = 'update'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/update.html'
    model = Bulletin
    form_class = BulletinForm

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
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug

        super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        context['title'] = _('Update Bulletin')

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject

        return context

    def get_success_url(self):
        messages.success(self.request, _('The Bulletin "%s" was updated successfully!')%(self.object.name))

        success_url = reverse_lazy('bulletin:view', kwargs = {'slug': self.object.slug})

        if self.object.show_window:
            self.request.session['resources'] = {}
            self.request.session['resources']['new_page'] = True
            self.request.session['resources']['new_page_url'] = reverse('bulletin:window_view', kwargs = {'slug': self.object.slug})

            success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

        return success_url

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = 'resources'
	log_action = 'delete'
	log_resource = 'bulletin'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'resources/delete.html'
	model = Bulletin
	context_object_name = 'resource'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		bulletin = get_object_or_404(Bulletin, slug = slug)

		if not has_subject_permissions(request.user, bulletin.topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(DeleteView, self).dispatch(request, *args, **kwargs)

	def get_success_url(self):
		messages.success(self.request, _('The bulletin "%s" was removed successfully from virtual environment "%s"!')%(self.object.name, self.object.topic.subject.name))

		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['bulletin_id'] = self.object.id
		self.log_context['bulletin_name'] = self.object.name
		self.log_context['bulletin_slug'] = self.object.slug

		super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})


class StatisticsView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view_statistics'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Bulletin
    template_name = 'bulletin/relatorios.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug = slug)

        if not has_subject_permissions(request.user, bulletin.topic.subject):
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
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug

        super(StatisticsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)


        context['title'] = _('Bulletin Reports')

        slug = self.kwargs.get('slug')
        bulletin = get_object_or_404(Bulletin, slug = slug)

        date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language','') == 'pt-br' else "%m/%d/%Y %I:%M %p"
        if self.request.GET.get('language','') == "":
            start_date = datetime.datetime.now() - datetime.timedelta(30)
            end_date = datetime.datetime.now()
        else :
            start_date = datetime.datetime.strptime(self.request.GET.get('init_date',''),date_format)
            end_date = datetime.datetime.strptime(self.request.GET.get('end_date',''),date_format)
        context["init_date"] = start_date
        context["end_date"] = end_date
        alunos = bulletin.students.all()
        if bulletin.all_students :
        	alunos = bulletin.topic.subject.students.all()

        vis_ou = Log.objects.filter(context__contains={'bulletin_id':bulletin.id},resource="bulletin",action="view",user_email__in=(aluno.email for aluno in alunos), datetime__range=(start_date,end_date + datetime.timedelta(minutes = 1)))
        did,n_did,history = str(_("Realized")),str(_("Unrealized")),str(_("Historic"))
        re = []
        data_n_did,data_history = [],[]
        json_n_did, json_history = {},{}

        for log_al in vis_ou.order_by("datetime"):
            data_history.append([str(alunos.get(email=log_al.user_email)),
            ", ".join([str(x) for x in bulletin.topic.subject.group_subject.filter(participants__email=log_al.user_email)]),
            log_al.action,log_al.datetime])

        json_history["data"] = data_history

        not_view = alunos.exclude(email__in=[log.user_email for log in vis_ou.distinct("user_email")])
        index = 0
        for alun in not_view:
            data_n_did.append([index,str(alun),", ".join([str(x) for x in bulletin.topic.subject.group_subject.filter(participants__email=alun.email)]),str(_('View')), str(alun.email)])
            index += 1
        json_n_did["data"] = data_n_did


        context["json_n_did"] = json_n_did
        context["json_history"] = json_history
        c_visualizou = vis_ou.distinct("user_email").count()
        column_view = str(_('View'))
        re.append([str(_('Bulletin')),did,n_did])
        re.append([column_view,c_visualizou, alunos.count() - c_visualizou])
        context['topic'] = bulletin.topic
        context['subject'] = bulletin.topic.subject
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
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/send_message.html'
    form_class = FormModalMessage

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug = slug)
        self.bulletin = bulletin

        if not has_subject_permissions(request.user, bulletin.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SendMessage, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        message = form.cleaned_data.get('comment')
        image = form.cleaned_data.get("image")
        users = (self.request.POST.get('users[]','')).split(",")
        user = self.request.user
        subject = self.bulletin.topic.subject

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
        context["bulletin"] = get_object_or_404(Bulletin, slug=self.kwargs.get('slug', ''))
        return context
