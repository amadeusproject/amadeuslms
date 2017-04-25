from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from amadeus.permissions import has_subject_permissions, has_resource_permissions

import time
import datetime
from log.models import Log
from log.mixins import LogMixin

from topics.models import Topic

from pendencies.forms import PendenciesForm

from .forms import WebpageForm
from .models import Webpage

class NewWindowView(LoginRequiredMixin, LogMixin, generic.DetailView):
	log_component = 'resources'
	log_action = 'view'
	log_resource = 'webpage'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webpages/window_view.html'
	model = Webpage
	context_object_name = 'webpage'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webpage = get_object_or_404(Webpage, slug = slug)

		if not has_resource_permissions(request.user, webpage):
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
		self.log_context['webpage_id'] = self.object.id
		self.log_context['webpage_name'] = self.object.name
		self.log_context['webpage_slug'] = self.object.slug
		self.log_context['timestamp_start'] = str(int(time.time()))

		super(NewWindowView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['log_id'] = Log.objects.latest('id').id

		return context

class InsideView(LoginRequiredMixin, LogMixin, generic.DetailView):
	log_component = 'resources'
	log_action = 'view'
	log_resource = 'webpage'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webpages/view.html'
	model = Webpage
	context_object_name = 'webpage'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webpage = get_object_or_404(Webpage, slug = slug)

		if not has_resource_permissions(request.user, webpage):
			return redirect(reverse_lazy('subjects:home'))

		return super(InsideView, self).dispatch(request, *args, **kwargs)

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
		self.log_context['webpage_id'] = self.object.id
		self.log_context['webpage_name'] = self.object.name
		self.log_context['webpage_slug'] = self.object.slug
		self.log_context['timestamp_start'] = str(int(time.time()))

		super(InsideView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['log_id'] = Log.objects.latest('id').id

		return context

class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = 'resources'
	log_action = 'create'
	log_resource = 'webpage'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webpages/create.html'
	form_class = WebpageForm

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
		self.log_context['webpage_id'] = self.object.id
		self.log_context['webpage_name'] = self.object.name
		self.log_context['webpage_slug'] = self.object.slug

		super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)

		context['title'] = _('Create Webpage')

		slug = self.kwargs.get('slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('The Webpage "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

		success_url = reverse_lazy('webpages:view', kwargs = {'slug': self.object.slug})

		if self.object.show_window:
			self.request.session['resources'] = {}
			self.request.session['resources']['new_page'] = True
			self.request.session['resources']['new_page_url'] = reverse('webpages:window_view', kwargs = {'slug': self.object.slug})

			success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

		return success_url

class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
	log_component = 'resources'
	log_action = 'update'
	log_resource = 'webpage'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'webpages/update.html'
	model = Webpage
	form_class = WebpageForm

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
		self.log_context['webpage_id'] = self.object.id
		self.log_context['webpage_name'] = self.object.name
		self.log_context['webpage_slug'] = self.object.slug

		super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return redirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)

		context['title'] = _('Update Webpage')

		slug = self.kwargs.get('topic_slug', '')
		topic = get_object_or_404(Topic, slug = slug)

		context['topic'] = topic
		context['subject'] = topic.subject

		return context

	def get_success_url(self):
		messages.success(self.request, _('The Webpage "%s" was updated successfully!')%(self.object.name))

		success_url = reverse_lazy('webpages:view', kwargs = {'slug': self.object.slug})

		if self.object.show_window:
			self.request.session['resources'] = {}
			self.request.session['resources']['new_page'] = True
			self.request.session['resources']['new_page_url'] = reverse('webpages:window_view', kwargs = {'slug': self.object.slug})

			success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

		return success_url

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = 'resources'
	log_action = 'delete'
	log_resource = 'webpage'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'resources/delete.html'
	model = Webpage
	context_object_name = 'resource'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		webpage = get_object_or_404(Webpage, slug = slug)

		if not has_subject_permissions(request.user, webpage.topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(DeleteView, self).dispatch(request, *args, **kwargs)

	def get_success_url(self):
		messages.success(self.request, _('The webpage "%s" was removed successfully from virtual environment "%s"!')%(self.object.name, self.object.topic.subject.name))

		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['webpage_id'] = self.object.id
		self.log_context['webpage_name'] = self.object.name
		self.log_context['webpage_slug'] = self.object.slug

		super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})


def get_chart(request,slug):
    webpage = get_object_or_404(Webpage, slug=slug)
    alunos = webpage.students.all()
    visualizou = Log.objects.filter(context__contains={'webpage_id':webpage.id},resource="webpage",action="view",user_email__in=(aluno.email for aluno in alunos)).distinct("user_email")
    re = []
    c_visualizou = visualizou.count()
    re.append(["Página Web","Fez","Não fez"])
    re.append(["Visualizar",c_visualizou, alunos.count() - c_visualizou])
    return JsonResponse({"dados":re})


class StatisticsView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view_statistics'
    log_resource = 'webpage'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Webpage
    template_name = 'webpages/relatorios.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        webpage = get_object_or_404(Webpage, slug = slug)

        if not has_subject_permissions(request.user, webpage.topic.subject):
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
        self.log_context['webpage_id'] = self.object.id
        self.log_context['webpage_name'] = self.object.name
        self.log_context['webpage_slug'] = self.object.slug

        super(StatisticsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)


        context['title'] = _('Webpage Reports')

        slug = self.kwargs.get('slug')
        webpage = get_object_or_404(Webpage, slug = slug)
        print (self.request.GET.get('init_date',''))
        date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language','') == 'pt-br' else "%m/%d/%Y %I:%M %p"
        if self.request.GET.get('language','') == "":
            start_date = datetime.datetime.now() - datetime.timedelta(30)
            end_date = datetime.datetime.now()
        else :
            start_date = datetime.datetime.strptime(self.request.GET.get('init_date',''),date_format)
            end_date = datetime.datetime.strptime(self.request.GET.get('end_date',''),date_format)
        print (start_date,"     depois")
        context["init_date"] = start_date
        context["end_date"] = end_date
        alunos = webpage.students.all()

        vis_ou = Log.objects.filter(context__contains={'webpage_id':webpage.id},resource="webpage",action="view",user_email__in=(aluno.email for aluno in alunos), datetime__range=(start_date,end_date + datetime.timedelta(minutes = 1)))
        did,n_did,history = str(_("Users who viewed")),str(_("Users who did not viewed")),str(_("History"))
        re = []
        data_did, data_n_did,data_history = [],[],[]
        json_did, json_n_did, json_history = {},{},{}
        # column = []
        # column.append([str(_("User")),"string"])
        # column.append([str(_("Group")),"string"])

        from django.db.models import Count, Max
        views_user = vis_ou.values("user_email").annotate(views=Count("user_email"))
        date_last = vis_ou.values("user_email").annotate(last=Max("datetime"))
        # column.append([str(_("Number of views")),"string"])
        # column.append([str(_("Date of last view")),"date"])
        for i in range(0,len(views_user)):
            data_did.append([str(alunos.get(email=views_user[i].get("user_email"))),
                ", ".join([str(x) for x in webpage.topic.subject.group_subject.filter(participants__email=views_user[i].get("user_email"))]),
                views_user[i].get("views"),date_last.get(user_email=views_user[i].get("user_email")).get("last")])
        json_did["data"] = data_did

        # column.append([str(_("Action")),"string"])
        # column.append([str(_("Date of action")),"date"])
        for log_al in vis_ou.order_by("datetime"):
            data_history.append([str(alunos.get(email=log_al.user_email)),
            ", ".join([str(x) for x in webpage.topic.subject.group_subject.filter(participants__email=log_al.user_email)]),
            log_al.action,log_al.datetime])
            json_history["data"] = data_history

        not_view = alunos.exclude(email__in=[log.user_email for log in vis_ou.distinct("user_email")])
        for alun in not_view:
            data_n_did.append([str(alun),", ".join([str(x) for x in webpage.topic.subject.group_subject.filter(participants__email=alun.email)])])
        json_n_did["data"] = data_n_did


        context["json_did"] = json_did
        context["json_n_did"] = json_n_did
        context["json_history"] = json_history
        c_visualizou = vis_ou.distinct("user_email").count()
        re.append([str(_('Webpage')),did,n_did])
        re.append([str(_('View')),c_visualizou, alunos.count() - c_visualizou])
        context['topic'] = webpage.topic
        context['subject'] = webpage.topic.subject
        context['db_data'] = re
        context['title_chart'] = _('Students viewing the web conference')
        context['title_vAxis'] = _('Quantity')

        context["n_did_table"] = n_did
        context["did_table"] = did
        context["history_table"] = history
        return context
