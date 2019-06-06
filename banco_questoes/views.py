from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from amadeus.permissions import has_subject_permissions
from subjects.models import Subject
from .forms import QuestionForm, AlternativeFormset
from .models import Question, valid_formats, CreateQuestionInDBLog, UpdateQuestionInDBLog, \
    ReplicateQuestionInDBLog, DeleteQuestionInDBLog


class IndexView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'banco_questoes/index.html'
    context_object_name = 'questions'
    paginate_by = 10
    totals = 0

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug=slug)

        if not has_subject_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug=slug)

        search = self.request.GET.get('search', '')

        if not search == '':
            cats = search.split(',')
            self.totals = Question.objects.filter(subject=subject,
                                                  categories__name__in=cats).count()

            return Question.objects.filter(subject=subject, categories__name__in=cats)

        self.totals = Question.objects.filter(subject=subject).count()

        return Question.objects.filter(subject=subject)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug=slug)

        context['title'] = _('Questions Database')
        context['subject'] = subject
        context['searched'] = self.request.GET.get('search', '')
        context['totals'] = self.totals

        return context


class QuestionCreateView(LoginRequiredMixin, CreateView):
    form_class = QuestionForm
    template_name = 'banco_questoes/create.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug=slug)

        if not has_subject_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(QuestionCreateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(QuestionCreateView, self).get_initial()

        if self.kwargs.get('question_id'):  # when the user replicate a question
            question = get_object_or_404(Question, pk=self.kwargs['question_id'])
            initial = initial.copy()
            initial['enunciado'] = question.enunciado
            initial['question_img'] = question.question_img
            initial['categories'] = ", ".join(
                question.categories.all().values_list("name", flat=True))

            replicate_log = ReplicateQuestionInDBLog()
            replicate_log.subject = self.object.subject
            replicate_log.user = self.request.user
            replicate_log.category = self.object.subject.category
            replicate_log.question = self.object
            replicate_log.save()

        return initial

    def get(self, request, *args, **kwargs):
        self.object = None

        form = self.get_form(self.get_form_class())

        if self.kwargs.get('question_id'):
            alternatives = AlternativeFormset(
                instance=get_object_or_404(Question, pk=self.kwargs['question_id']))
        else:
            alternatives = AlternativeFormset()

        return self.render_to_response(self.get_context_data(form=form, formset=alternatives))

    def post(self, *args, **kwargs):
        self.object = None

        form = self.get_form(self.get_form_class())

        alternatives = AlternativeFormset(self.request.POST, self.request.FILES)

        if form.is_valid() and alternatives.is_valid():
            return self.form_valid(form, alternatives)
        else:
            return self.form_invalid(form, alternatives)

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def form_valid(self, form, formset):
        self.object = form.save(commit=False)

        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug=slug)

        self.object.subject = subject

        self.object.save()

        alternatives = formset.save(commit=False)

        for alt in alternatives:
            alt.question = self.object

            alt.save()

        create_question_in_db_log = CreateQuestionInDBLog()
        create_question_in_db_log.subject = self.object.subject
        create_question_in_db_log.user = self.request.user
        create_question_in_db_log.category = self.object.subject.category
        create_question_in_db_log.question = self.object
        create_question_in_db_log.save()

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(QuestionCreateView, self).get_context_data(**kwargs)

        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug=slug)

        context["title"] = _('Create Question')
        context["subject"] = subject
        context["mimeTypes"] = valid_formats

        return context

    def get_success_url(self):
        messages.success(self.request, _(
            'The Question was added to the virtual environment "%s" successfully!') % (
                             self.object.subject.name))

        return reverse_lazy('questions_database:index', kwargs={'slug': self.object.subject.slug})


class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'banco_questoes/create.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    context_object_name = 'question'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug=slug)

        if not has_subject_permissions(request.user, subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(QuestionUpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(self.get_form_class())
        alternatives = AlternativeFormset(instance=self.object)

        return self.render_to_response(self.get_context_data(form=form, formset=alternatives))

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(self.get_form_class())
        alternatives = AlternativeFormset(self.request.POST, self.request.FILES,
                                          instance=self.object)

        if form.is_valid() and alternatives.is_valid():
            return self.form_valid(form, alternatives)
        else:
            return self.form_invalid(form, alternatives)

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def form_valid(self, form, formset):
        self.object = form.save(commit=False)

        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug=slug)

        self.object.subject = subject
        self.object.save()

        alternatives = formset.save(commit=False)

        for alt in alternatives:
            alt.question = self.object
            alt.save()

        update_log = UpdateQuestionInDBLog(category=self.object.subject.category,
                                           subject=self.object.subject,
                                           question=self.object,
                                           user=self.request.user)
        update_log.save()
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(QuestionUpdateView, self).get_context_data(**kwargs)

        slug = self.kwargs.get('slug', '')
        subject = get_object_or_404(Subject, slug=slug)

        context["title"] = _('Edit Question')
        context["subject"] = subject
        context["mimeTypes"] = valid_formats

        return context

    def get_success_url(self):
        messages.success(self.request, _('The Question was updated successfully!'))

        return reverse_lazy('questions_database:index', kwargs={'slug': self.object.subject.slug})


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'banco_questoes/delete.html'
    model = Question
    context_object_name = 'question'

    def dispatch(self, request, *args, **kwargs):
        id = self.kwargs.get('pk', '')
        question = get_object_or_404(Question, pk=id)

        if not has_subject_permissions(request.user, question.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(QuestionDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, _(
            'The question was removed successfully from virtual environment "%s"!') % (
                             self.object.subject.name))

        delete_log = DeleteQuestionInDBLog(category=self.object.subject.category,
                                           subject=self.object.subject,
                                           user=self.request.user,
                                           question=self.object)
        delete_log.save()
        return reverse_lazy('questions_database:index', kwargs={'slug': self.object.subject.slug})
