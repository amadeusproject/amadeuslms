from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Question

from subjects.models import Subject

# Create your views here.
class IndexView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'banco_questoes/index.html'
    context_object_name = 'questions'
    paginate_by = 10

    def get_queryset(self):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        return Question.objects.filter(subject = subject)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        context['title'] = _('Questions Database')
        context['subject'] = subject

        return context
    
    