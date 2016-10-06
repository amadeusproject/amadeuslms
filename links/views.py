# from django.shortcuts import render
# from django.views import generic
# from django.core.urlresolvers import reverse_lazy
# from django.contrib import messages
# from django.utils.translation import ugettext_lazy as _
#
#
# from .models import Link
# from .forms import *
#
# # Create your views here.
# class CreateLink(generic.CreateView):
#     template_name = 'links/'
#     form_class = CreateLinkForm
#     success_url = reverse_lazy()
#     def form_valid(self, form):
# 		form.save()
# 		messages.success(self.request, _('Link created successfully!'))
# 		return super(CreateLink, self).form_valid(form)
#
#
# class DeleteLink(generic.DeleteView):
#
# class UpdateLink(generic.UpdateView):
#     template_name = 'links/'
#     form_class = UpdateLinkForm
#     success_url = reverse_lazy()
#     def form_valid(self, form):
# 		form.save()
# 		messages.success(self.request, _('Link updated successfully!'))
#
# 		return super(UpdateLink, self).form_valid(form)
