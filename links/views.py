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
    template_name = 'links/link_modal.html'
    form_class = CreateLinkForm
    success_url = reverse_lazy('course:manage')
    context_object_name = 'links'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Link created successfully!'))
        return super(CreateLink, self).form_valid(form)
    def get_context_data(self, **kwargs):
    	context = {}
    	context['links'] = Link.objects.all()
    	return context


def deleteLink(request,linkname):
    link = get_object_or_404(Link,name = linkname)
    link.delete()
    messages.success(request,_("Link deleted Successfully!"))
    return redirect('course:manage')
class UpdateLink(generic.UpdateView):
    template_name = 'links/'
    form_class = UpdateLinkForm
    success_url = reverse_lazy()
    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Link updated successfully!'))

        return super(UpdateLink, self).form_valid(form)
