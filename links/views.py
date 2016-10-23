from django.shortcuts import render
from django.views import generic
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from rolepermissions.mixins import HasRoleMixin

from courses.models import Topic
from .models import Link
from .forms import *

# Create your views here.
class CreateLink(LoginRequiredMixin, HasRoleMixin, generic.CreateView):
    allowed_roles = ['professor', 'system_admin']
    template_name = 'links/create_link.html'
    form_class = CreateLinkForm
    success_url = reverse_lazy('course:manage')
    context_object_name = 'form'

    def form_valid(self, form):
        self.object = form.save(commit = False)
        topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
        self.object.topic = topic
        messages.success(self.request, _('Link created successfully!'))
        #messages.error(self.request, _("An error occurred when trying to create the link"))
        self.object.save()
        #return self.success_url
        return self.get_success_url()
    def get_context_data(self,**kwargs):
        context = {}
        context['links'] = Link.objects.all()
        context['form'] = CreateLinkForm
        topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
        context["topic"] = topic
        return context
    def get_success_url(self):
        self.success_url = redirect('course:links:render_link', id = self.object.id)
        return self.success_url
def deleteLink(request,linkname):
    link = get_object_or_404(Link,name = linkname)
    link.delete()
    template_name = 'links/delete_link.html'
    messages.success(request,_("Link deleted Successfully!"))
    #messages.error(request, _("An error occurred when trying to delete the link"))
    return redirect('course:manage')

def render_link(request, id):
	template_name = 'links/render_link.html'
	context = {
		'link': get_object_or_404(Link, id = id)
	}
	return render(request, template_name, context)

#Referencia no delete link para adicionar quando resolver o problema do context {% url 'course:delete' link.name  %}
class UpdateLink(LoginRequiredMixin, HasRoleMixin, generic.UpdateView):
    allowed_roles = ['professor', 'system_admin']
    template_name = 'links/update_link.html'
    form_class = UpdateLinkForm
    success_url = reverse_lazy('course:links:render_link')
    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Link updated successfully!'))

        return super(UpdateLink, self).form_valid(form)

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Link, slug = self.kwargs.get('slug'))
        print(self.object.link_description)
        return self.object
    def get_success_url(self):
        self.success_url = redirect('course:links:render_link', id = self.object.id)
        return self.success_url
class ViewLink(LoginRequiredMixin,HasRoleMixin,generic.DetailView):
    allowed_roles = ['professor', 'system_admin']
    template_name = 'links/view_link.html'
    success_url = reverse_lazy('course:links:render_link')
    context_object_name = 'link'
    def get_context_data(self,**kwargs):
        context = {}
        link = Link.objects.get(slug = self.kwargs.get('slug'))
        context['link'] = link
        return context
    def get_success_url(self):
        self.success_url = redirect('course:links:render_link', id = self.object.id)
        return self.success_url
    def get_queryset(self):
        self.queryset = Link.objects.filter(slug = self.kwargs.get('slug'))
        return self.queryset
