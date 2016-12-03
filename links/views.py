from django.shortcuts import render
from django.views import generic
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from rolepermissions.mixins import HasRoleMixin
from core.mixins import NotificationMixin
from django.urls import reverse
from django.core.files.base import ContentFile
from rolepermissions.verifications import has_role
import time

from core.models import Log
from core.mixins import LogMixin
from core.decorators import log_decorator

from .image_crawler import *
from courses.models import Topic
from .models import Link
from .forms import *


# Create your views here.
class CreateLink(LoginRequiredMixin, HasRoleMixin, LogMixin, NotificationMixin, generic.CreateView):
    log_component = 'link'
    log_resource = 'link'
    log_action = 'create'
    log_context = {}

    allowed_roles = ['professor', 'system_admin']
    template_name = 'links/create_link.html'
    form_class = CreateLinkForm
    success_url = reverse_lazy('course:manage')
    context_object_name = 'form'

    def form_invalid(self,form):
        context = super(CreateLink, self).form_invalid(form)
        context.status_code = 400

        return context

    def form_valid(self, form):
        self.object = form.save(commit = False)
        topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
        self.object.topic = topic
        self.object.save()
        self.link = Link.objects.get(slug = self.object.slug)
        try:
            self.formato,self.baixado = get_images(self.link.link_url,self.link.slug)
            self.caminho = 'links/static/images/%s'%(self.link.slug)+'%s'%(self.formato)
        except Exception:
            self.baixado = False


        super(CreateLink, self).createNotification(message="created a Link at "+ self.object.topic.name, actor=self.request.user,
            resource_name=self.object.name, resource_link= reverse('course:view_topic', args=[self.object.topic.slug]),
            users=self.object.topic.subject.students.all())

        self.log_context['link_id'] = self.object.id
        self.log_context['link_name'] = self.object.name
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['course_id'] = self.object.topic.subject.course.id
        self.log_context['course_name'] = self.object.topic.subject.course.name
        self.log_context['course_slug'] = self.object.topic.subject.course.slug
        self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
        self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

        super(CreateLink, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        self.setImage()

        return self.get_success_url()

    def setImage(self):
        if self.baixado:
            with open(self.caminho,'rb') as f:
                data = f.read()
            nome = '%s'%(self.link.slug)+"%s"%(self.formato)
            self.link.image.save(nome,ContentFile(data))
        else:
            with open('links/static/images/default.jpg','rb') as f:
                data = f.read()
            self.link.image.save('default.jpg',ContentFile(data))

    def get_context_data(self,**kwargs):
        context = {}
        context['links'] = Link.objects.all()
        context['form'] = CreateLinkForm
        topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
        context["topic"] = topic
        return context

    def get_success_url(self):
        self.success_url = redirect('course:links:render_link', slug = self.object.slug)
        return self.success_url

class DeleteLink(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.DeleteView):
    log_component = 'link'
    log_resource = 'link'
    log_action = 'delete'
    log_context = {}

    allowed_roles = ['professor', 'system_admin']
    login_url = reverse_lazy("core:home")
    redirect_field_name = 'next'
    model = Link
    template_name = 'links/delete_link.html'

    def dispatch(self, *args, **kwargs):
        link = get_object_or_404(Link, slug = self.kwargs.get('slug'))
        if(not (has_role(self.request.user, 'professor')) or not(has_role(self.request.user, 'system_admin')) ):
            return self.handle_no_permission()
        return super(DeleteLink, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteLink, self).get_context_data(**kwargs)
        context['course'] = self.object.topic.subject.course
        context['subject'] = self.object.topic.subject
        context['link'] = self.object
        context["topic"] = self.object.topic
        return context

    def get_success_url(self):
        self.log_context['link_id'] = self.object.id
        self.log_context['link_name'] = self.object.name
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['course_id'] = self.object.topic.subject.course.id
        self.log_context['course_name'] = self.object.topic.subject.course.name
        self.log_context['course_slug'] = self.object.topic.subject.course.slug
        self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
        self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

        super(DeleteLink, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return reverse_lazy('course:view_topic', kwargs={'slug' : self.object.topic.slug})

def render_link(request, slug):
	template_name = 'links/render_link.html'
	context = {
		'link': get_object_or_404(Link, slug = slug)
	}
	return render(request, template_name, context)

#Referencia no delete link para adicionar quando resolver o problema do context {% url 'course:delete' link.name  %}
class UpdateLink(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.UpdateView):
    log_component = 'link'
    log_resource = 'link'
    log_action = 'update'
    log_context = {}

    allowed_roles = ['professor', 'system_admin']
    template_name = 'links/update_link.html'
    form_class = UpdateLinkForm
    success_url = reverse_lazy('course:links:render_link')

    def form_invalid(self,form):
        context = super(UpdateLink, self).form_invalid(form)
        context.status_code = 400

        return context

    def form_valid(self, form):
        formulario = form
        if formulario.has_changed():
            if  'link_url' in formulario.changed_data:
                self.object = form.save()
                self.link = Link.objects.get(slug = self.object.slug)
                self.formato,self.baixado = get_images(self.link.link_url,self.link.slug)
                self.caminho = 'links/static/images/%s'%(self.link.slug)+'%s'%(self.formato)
                self.setImage()
            else:
                self.object = form.save()
        else:
            self.object = form.save()

        self.log_context['link_id'] = self.object.id
        self.log_context['link_name'] = self.object.name
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['course_id'] = self.object.topic.subject.course.id
        self.log_context['course_name'] = self.object.topic.subject.course.name
        self.log_context['course_slug'] = self.object.topic.subject.course.slug
        self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
        self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

        super(UpdateLink, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return super(UpdateLink, self).form_valid(form)

    def setImage(self):
        if self.baixado:
            with open(self.caminho,'rb') as f:
                data = f.read()
            nome = '%s'%(self.link.slug)+"%s"%(self.formato)
            self.object.image.save(nome,ContentFile(data))
        else:
            with open('links/static/images/default.jpg','rb') as f:
                data = f.read()
            self.object.image.save('default.jpg',ContentFile(data))
    def get_object(self, queryset=None):
        self.object = get_object_or_404(Link, slug = self.kwargs.get('slug'))
        return self.object
    def get_success_url(self):
        self.success_url = reverse_lazy('course:links:render_link', args = (self.object.slug, ))
        return self.success_url

class ViewLink(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.DetailView):
    log_component = 'link'
    log_resource = 'link'
    log_action = 'viewed'
    log_context = {}

    allowed_roles = ['professor', 'system_admin']
    template_name = 'links/view_link.html'
    success_url = reverse_lazy('course:links:render_link')
    context_object_name = 'link'

    def get_context_data(self,**kwargs):
        context = {}
        link = Link.objects.get(slug = self.kwargs.get('slug'))
        context['link'] = link

        self.log_context['link_id'] = link.id
        self.log_context['link_name'] = link.name
        self.log_context['topic_id'] = link.topic.id
        self.log_context['topic_name'] = link.topic.name
        self.log_context['topic_slug'] = link.topic.slug
        self.log_context['subject_id'] = link.topic.subject.id
        self.log_context['subject_name'] = link.topic.subject.name
        self.log_context['subject_slug'] = link.topic.subject.slug
        self.log_context['course_id'] = link.topic.subject.course.id
        self.log_context['course_name'] = link.topic.subject.course.name
        self.log_context['course_slug'] = link.topic.subject.course.slug
        self.log_context['course_category_id'] = link.topic.subject.course.category.id
        self.log_context['course_category_name'] = link.topic.subject.course.category.name
        self.log_context['timestamp_start'] = str(int(time.time()))

        super(ViewLink, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return context

    def get_success_url(self):
        self.success_url = redirect('course:links:render_link', slug = self.object.slug)

        return self.success_url

    def get_queryset(self):
        self.queryset = Link.objects.filter(slug = self.kwargs.get('slug'))
        return self.queryset
