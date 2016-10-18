from django.shortcuts import render
from django.views import generic
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404,redirect

from .models import Link
from .forms import *

# Create your views here.
class CreateLink(generic.CreateView):
    template_name = 'links/create_link.html'
    form_class = CreateLinkForm
    success_url = reverse_lazy('course:manage')
    context_object_name = 'form'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Link created successfully!'))
        messages.error(self.request, _("An error occurred when trying to create the link"))
        return super(CreateLink, self).form_valid(form)
    def get_context_data(self,**kwargs):
        context = {}
        context['links'] = Link.objects.all()
        context['form'] = CreateLinkForm
        return context

def deleteLink(request,linkname):
    link = get_object_or_404(Link,name = linkname)
    link.delete()
    template_name = 'links/delete_link.html'
    messages.success(request,_("Link deleted Successfully!"))
    messages.error(request, _("An error occurred when trying to delete the link"))
    return redirect('course:manage')
#Referencia no delete link para adicionar quando resolver o problema do context {% url 'course:delete' link.name  %}
class UpdateLink(generic.UpdateView):
    template_name = 'links/update_link.html'
    form_class = UpdateLinkForm
    success_url = reverse_lazy('course:manage')
    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Link updated successfully!'))

        return super(UpdateLink, self).form_valid(form)
