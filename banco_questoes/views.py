from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.views.generic import ListView, CreateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.mixins import LoginRequiredMixin
from log.mixins import LogMixin

from .models import Question, valid_formats
from .forms import QuestionForm, AlternativeFormset

from subjects.models import Subject

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
    
class QuestionCreateView(LoginRequiredMixin, LogMixin, CreateView):
    form_class = QuestionForm
    template_name = 'banco_questoes/create.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    log_component = 'questions_database'
    log_resource = 'questions_database'
    log_action = 'create'
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        return super(QuestionCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None

        form = self.get_form(self.get_form_class())

        alternatives = AlternativeFormset()

        return self.render_to_response(self.get_context_data(form = form, formset = alternatives))

    def post(self, *args, **kwargs):
        self.object = None

        form = self.get_form(self.get_form_class())

        alternatives = AlternativeFormset(self.request.POST)

        if (form.is_valid() and alternatives.is_valid()):
            return self.form_valid(form, alternatives)
        else:
            return self.form_invalid(form, alternatives)

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form = form, formset = formset))

    def form_valid(self, form, formset):
        self.object = form.save(commit = False)

        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)

        self.object.subject = subject

        self.object.save()

        alternatives = formset.save(commit = False)

        for alt in alternatives:
            alt.question = self.object

            alt.save()

        self.log_context['category_id'] = self.object.subject.category.id
        self.log_context['category_name'] = self.object.subject.category.name
        self.log_context['category_slug'] = self.object.subject.category.slug
        self.log_context['subject_id'] = self.object.subject.id
        self.log_context['subject_name'] = self.object.subject.name
        self.log_context['subject_slug'] = self.object.subject.slug
        self.log_context['question_id'] = self.object.id
        self.log_context['question_content'] = self.object.enunciado

        super(QuestionCreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(QuestionCreateView, self).get_context_data(**kwargs)

        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug = slug)
        
        context["title"] = _('Create Question')
        context["subject"] = subject
        context["mimTypes"] = valid_formats

        return context
    
    def get_success_url(self):
        messages.success(self.request, _('The Question was added to the virtual environment "%s" successfully!')%(self.object.subject.name))

        return reverse_lazy('questions_database:index', kwargs = {'slug': self.object.subject.slug})