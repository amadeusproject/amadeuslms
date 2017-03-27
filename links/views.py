from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Link
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
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


class DetailLinkView(LoginRequiredMixin, LogMixin, generic.detail.DetailView):
    log_component = 'resources'
    log_action = 'view'
    log_resource = 'link'
    log_context = {}
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    model = Link
    template_name = 'links/view.html'
    context_object_name = 'web_link'

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

        return context

    def get_success_url(self):
        messages.success(self.request, _('The Website Link "%s" was updated successfully!')%(self.object.name))

        return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})
