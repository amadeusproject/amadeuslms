
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
from django.http import HttpResponse, Http404

from log.mixins import LogMixin
from topics.models import Topic, Resource
from .models import PDFFile
from pendencies.forms import PendenciesForm



class ViewPDFFile(LoginRequiredMixin, LogMixin, generic.TemplateView):
    template_name='pdf_file/view.html'
    log_component = 'resources'
    log_action = 'view'
    log_resource = 'pdf_file'
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
        self.log_context['pdf_id'] = pdf_file.id
        self.log_context['pdf_name'] = pdf_file.name
        self.log_context['pdf_slug'] = pdf_file.slug

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
        self.log_context['pdf_file_id'] = self.object.id
        self.log_context['pdf_file_name'] = self.object.name
        self.log_context['pdf_file_slug'] = self.object.slug

        super(PDFFileCreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(PDFFileCreateView, self).get_context_data(**kwargs)

        context['title'] = _('Create PDF File')

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject

        return context

    def get_success_url(self):
        messages.success(self.request, _('The PDF File "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

        return reverse_lazy('subjects:topic_view', kwargs = {'slug': self.object.topic.subject.slug, 'topic_slug': self.object.topic.slug})


class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    log_component = 'resources'
    log_action = 'update'
    log_resource = 'pdf_file'
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
        self.log_context['pdf_file_id'] = self.object.id
        self.log_context['pdf_file_name'] = self.object.name
        self.log_context['pdf_file_slug'] = self.object.slug

        super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        context['title'] = _('Update PDF File')

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject

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
        self.log_context['pdf_file_id'] = self.object.id
        self.log_context['pdf_file_name'] = self.object.name
        self.log_context['pdf_file_slug'] = self.object.slug

        super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})



