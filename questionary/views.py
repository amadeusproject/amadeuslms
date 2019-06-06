""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import json
import random
import textwrap
import time
from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import formats, timezone
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from amadeus.permissions import has_resource_permissions, \
    has_subject_permissions
from banco_questoes.models import Alternative, Question
from chat.models import Conversation, TalkMessages, ChatVisualizations
from log.decorators import log_decorator
from log.models import Log
from topics.models import Topic
from users.models import User
from webpage.forms import FormModalMessage
from .forms import InlinePendenciesFormset, InlineSpecificationFormset, \
    QuestionaryForm
from .models import Questionary, UserAnswer, UserQuest


class InsideView(LoginRequiredMixin, generic.ListView):
    log_component = "resources"
    log_action = "view"
    log_resource = "questionary"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'questionary/view.html'
    model = Questionary
    context_object_name = 'questionary'

    students = None
    userquest = None
    userquestions = None

    def get_queryset(self):
        slug = self.kwargs.get('slug', '')
        questionary = get_object_or_404(Questionary, slug=slug)

        if has_subject_permissions(self.request.user, questionary.topic.subject):
            if questionary.all_students:
                self.students = User.objects.filter(
                    subject_student=questionary.topic.subject).order_by('social_name', 'username')
            else:
                self.students = User.objects.filter(resource_students=questionary).order_by(
                    'social_name', 'username')

            self.userquest = UserQuest.objects.filter(student=self.students.first(),
                                                      questionary=questionary)

            if self.userquest:
                self.userquest = self.userquest.get()
                self.userquestions = UserAnswer.objects.filter(user_quest=self.userquest).order_by(
                    'order')
        else:
            self.userquest = UserQuest.objects.filter(student=self.request.user,
                                                      questionary=questionary)
            if self.userquest:
                self.userquest = self.userquest.get()
                self.userquestions = UserAnswer.objects.filter(user_quest=self.userquest).order_by(
                    'order')
            else:
                self.userquest = UserQuest.objects.create(student=self.request.user,
                                                          questionary=questionary)
                q_ids = [0]
                entries = []

                for specs in questionary.spec_questionary.all():
                    cats = list(specs.categories.values_list('id', flat=True))
                    n_questions = specs.n_questions

                    with connection.cursor() as cursor:
                        cursor.execute(
                            'SELECT DISTINCT question_id FROM banco_questoes_question_categories AS a WHERE %s <@ (SELECT array_agg(tag_id) FROM public.banco_questoes_question_categories AS c WHERE c.question_id = a.question_id) AND NOT a.question_id = any(%s)',
                            [cats, q_ids])
                        rows = cursor.fetchall()

                        list_q = []

                        for row in rows:
                            list_q.append(row[0])

                        random.shuffle(list_q)

                        q_ids = q_ids + (list_q[0:n_questions])

                questions = Question.objects.filter(pk__in=q_ids)

                orders = list(range(1, questions.count() + 1))
                random.shuffle(orders)

                for question in questions.all():
                    entries.append(
                        UserAnswer(user_quest=self.userquest, question=question, order=orders[0]))

                    orders.pop(0)

                UserAnswer.objects.bulk_create(entries)

                self.userquestions = UserAnswer.objects.filter(user_quest=self.userquest).order_by(
                    'order')

        return questionary

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        questionary = get_object_or_404(Questionary, slug=slug)

        user = request.POST.get('selected_student', None)

        self.object_list = questionary

        if has_subject_permissions(request.user, questionary.topic.subject):
            if questionary.all_students:
                self.students = User.objects.filter(
                    subject_student=questionary.topic.subject).order_by('social_name', 'username')
            else:
                self.students = User.objects.filter(resource_students=questionary).order_by(
                    'social_name', 'username')

            if user is not None:
                self.userquest = UserQuest.objects.filter(student__email=user,
                                                          questionary=questionary)

                if self.userquest:
                    self.userquest = self.userquest.get()
                    self.userquestions = UserAnswer.objects.filter(
                        user_quest=self.userquest).order_by('order')
            else:
                self.userquest = UserQuest.objects.filter(student=self.students.first(),
                                                          questionary=questionary)

                if self.userquest:
                    self.userquest = self.userquest.get()
                    self.userquestions = UserAnswer.objects.filter(
                        user_quest=self.userquest).order_by('order')

        return self.render_to_response(self.get_context_data())

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        questionary = get_object_or_404(Questionary, slug=slug)

        if not has_resource_permissions(request.user, questionary):
            return redirect(reverse_lazy('subjects:home'))

        if not has_subject_permissions(self.request.user, questionary.topic.subject):
            if timezone.now() < questionary.data_ini:
                messages.error(self.request, _(
                    'The questionary "%s" from topic "%s" can only be answered after %s' % (
                        str(questionary), str(questionary.topic),
                        (formats.date_format(questionary.data_ini, "SHORT_DATETIME_FORMAT")))))

                return redirect(
                    reverse_lazy('subjects:view', kwargs={"slug": questionary.topic.subject.slug}))

        return super(InsideView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        window = self.kwargs.get('window', None)

        template_name = 'questionary/view.html'

        if window:
            template_name = 'questionary/window_view.html'

        print(template_name)

        return template_name

    def get_context_data(self, **kwargs):
        context = super(InsideView, self).get_context_data(**kwargs)

        slug = self.kwargs.get('slug', '')
        questionary = get_object_or_404(Questionary, slug=slug)

        context['title'] = questionary.name

        context['questionary'] = questionary
        context['topic'] = questionary.topic
        context['subject'] = questionary.topic.subject
        context['userquest'] = self.userquest
        context['userquestions'] = self.userquestions

        if self.userquestions:
            context['useranswered'] = self.userquestions.filter(answer__isnull=False).count()
            context['usercorrect'] = self.userquestions.filter(is_correct=True).count()

        if self.students is not None:
            context['sub_students'] = self.students
            context['student'] = self.request.POST.get('selected_student',
                                                       self.students.first().email)

        self.log_context['category_id'] = questionary.topic.subject.category.id
        self.log_context['category_name'] = questionary.topic.subject.category.name
        self.log_context['category_slug'] = questionary.topic.subject.category.slug
        self.log_context['subject_id'] = questionary.topic.subject.id
        self.log_context['subject_name'] = questionary.topic.subject.name
        self.log_context['subject_slug'] = questionary.topic.subject.slug
        self.log_context['topic_id'] = questionary.topic.id
        self.log_context['topic_name'] = questionary.topic.name
        self.log_context['topic_slug'] = questionary.topic.slug
        self.log_context['questionary_id'] = questionary.id
        self.log_context['questionary_name'] = questionary.name
        self.log_context['questionary_slug'] = questionary.slug
        self.log_context['timestamp_start'] = str(int(time.time()))

        super(InsideView, self).create_log(self.request.user, self.log_component, self.log_action,
                                           self.log_resource)

        self.request.session['log_id'] = Log.objects.latest('id').id

        return context


class QuestionaryCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = QuestionaryForm
    template_name = 'questionary/create.html'

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    log_component = 'resources'
    log_resource = 'questionary'
    log_action = 'create'
    log_context = {}

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        questions = Question.objects.filter(subject=topic.subject)

        if not questions.exists():
            messages.error(self.request, _(
                'The questions database is empty. Before creating a new questionary you must provide questions to the questions database'))

            return redirect(reverse_lazy('subjects:view', kwargs={'slug': topic.subject.slug}))

        return super(QuestionaryCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        pendencies_form = InlinePendenciesFormset(initial=[{'subject': topic.subject.id,
                                                            'actions': [("", "-------"),
                                                                        ("start", _("Start")),
                                                                        ("view", _("Visualize")),
                                                                        ("finish", _("Finish"))]}])
        specifications_form = InlineSpecificationFormset(initial=[{'subject': topic.subject}])

        return self.render_to_response(
            self.get_context_data(form=form, pendencies_form=pendencies_form,
                                  specifications_form=specifications_form))

    def post(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        pendencies_form = InlinePendenciesFormset(self.request.POST, initial=[
            {'subject': topic.subject.id,
             'actions': [("", "-------"), ("view", _("Visualize")), ("finish", _("Finish"))]}])
        specifications_form = InlineSpecificationFormset(self.request.POST,
                                                         initial=[{'subject': topic.subject}])

        if form.is_valid() and pendencies_form.is_valid() and specifications_form.is_valid():
            return self.form_valid(form, pendencies_form, specifications_form)
        else:
            return self.form_invalid(form, pendencies_form, specifications_form)

    def form_invalid(self, form, pendencies_form, specifications_form):
        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        for p_form in pendencies_form.forms:
            p_form.fields['action'].choices = [("", "-------"), ("start", _("Start")),
                                               ("view", _("Visualize")), ("finish", _("Finish"))]

        return self.render_to_response(
            self.get_context_data(form=form, pendencies_form=pendencies_form,
                                  specifications_form=specifications_form))

    def form_valid(self, form, pendencies_form, specifications_form):
        self.object = form.save(commit=False)

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        self.object.topic = topic
        self.object.order = topic.resource_topic.count() + 1

        if not self.object.topic.visible and not self.object.topic.repository:
            self.object.visible = False

        self.object.save()

        pendencies_form.instance = self.object
        pendencies_form.save(commit=False)

        for pform in pendencies_form.forms:
            pend_form = pform.save(commit=False)

            if not pend_form.action == "":
                pend_form.save()

        specifications_form.instance = self.object
        specifications_form.save(commit=False)

        for sform in specifications_form.forms:
            spec_form = sform.save(commit=True)

            if not spec_form.n_questions or spec_form.n_questions == "":
                spec_form.delete()

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['questionary_id'] = self.object.id
        self.log_context['questionary_name'] = self.object.name
        self.log_context['questionary_slug'] = self.object.slug

        super(QuestionaryCreateView, self).create_log(self.request.user, self.log_component,
                                                      self.log_action, self.log_resource)

        return redirect(self.get_success_url())

    def get_initial(self):
        initial = super(QuestionaryCreateView, self).get_initial()

        slug = self.kwargs.get('slug', '')

        topic = get_object_or_404(Topic, slug=slug)
        initial['subject'] = topic.subject
        initial['topic'] = topic

        return initial

    def get_context_data(self, **kwargs):
        context = super(QuestionaryCreateView, self).get_context_data(**kwargs)

        context['title'] = _('Create Questionary')

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        context['topic'] = topic
        context['subject'] = topic.subject

        return context

    def get_success_url(self):
        messages.success(self.request,
                         _('The questionary %s was successfully created in the topic %s!') % (
                             self.object.name, self.object.topic.name))

        success_url = reverse_lazy('questionary:view', kwargs={'slug': self.object.slug})

        if self.object.show_window:
            self.request.session['resources'] = {}
            self.request.session['resources']['new_page'] = True
            self.request.session['resources']['new_page_url'] = reverse('questionary:window_view',
                                                                        kwargs={
                                                                            'slug': self.object.slug,
                                                                            'window': 'window'})

            success_url = reverse_lazy('subjects:view',
                                       kwargs={'slug': self.object.topic.subject.slug})

        return success_url


class UpdateView(LoginRequiredMixin, generic.UpdateView):
    log_component = "resources"
    log_action = "update"
    log_resource = "questionary"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'questionary/update.html'
    model = Questionary
    form_class = QuestionaryForm
    context_object_name = 'questionary'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        pendencies_form = InlinePendenciesFormset(instance=self.object, initial=[
            {'subject': topic.subject.id,
             'actions': [("", "-------"), ("start", _("Start")), ("view", _("Visualize")),
                         ("finish", _("Finish"))]}])
        specifications_form = InlineSpecificationFormset(instance=self.object,
                                                         initial=[{'subject': topic.subject}])

        return self.render_to_response(
            self.get_context_data(form=form, pendencies_form=pendencies_form,
                                  specifications_form=specifications_form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        pendencies_form = InlinePendenciesFormset(self.request.POST, instance=self.object, initial=[
            {'subject': topic.subject.id,
             'actions': [("", "-------"), ("start", _("Start")), ("view", _("Visualize")),
                         ("finish", _("Finish"))]}])
        specifications_form = InlineSpecificationFormset(self.request.POST, instance=self.object,
                                                         initial=[{'subject': topic.subject}])

        if (form.is_valid() and pendencies_form.is_valid() and specifications_form.is_valid()):
            return self.form_valid(form, pendencies_form, specifications_form)
        else:
            return self.form_invalid(form, pendencies_form, specifications_form)

    def form_invalid(self, form, pendencies_form, specifications_form):
        for p_form in pendencies_form.forms:
            p_form.fields['action'].choices = [("", "-------"), ("view", _("Visualize")),
                                               ("finish", _("Finish"))]

        return self.render_to_response(
            self.get_context_data(form=form, pendencies_form=pendencies_form,
                                  specifications_form=specifications_form))

    def form_valid(self, form, pendencies_form, specifications_form):
        self.object = form.save(commit=False)

        if not self.object.topic.visible and not self.object.topic.repository:
            self.object.visible = False

        self.object.save()

        pendencies_form.instance = self.object
        pendencies_form.save(commit=False)

        for form in pendencies_form.forms:
            pend_form = form.save(commit=False)

            if not pend_form.action == "":
                pend_form.save()

        specifications_form.instance = self.object
        specifications_form.save(commit=False)

        for sform in specifications_form.forms:
            spec_form = sform.save(commit=True)

            if not spec_form.n_questions or spec_form.n_questions == "":
                spec_form.delete()

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['questionary_id'] = self.object.id
        self.log_context['questionary_name'] = self.object.name
        self.log_context['questionary_slug'] = self.object.slug

        super(UpdateView, self).create_log(self.request.user, self.log_component, self.log_action,
                                           self.log_resource)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        context['title'] = _('Update Questionary')

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug=slug)

        context['topic'] = topic
        context['subject'] = topic.subject

        return context

    def get_success_url(self):
        messages.success(self.request,
                         _('The questionary %s of the topic %s was updated successfully!') % (
                             self.object.name, self.object.topic.name))

        success_url = reverse_lazy('questionary:view', kwargs={'slug': self.object.slug})

        if self.object.show_window:
            self.request.session['resources'] = {}
            self.request.session['resources']['new_page'] = True
            self.request.session['resources']['new_page_url'] = reverse('questionary:window_view',
                                                                        kwargs={
                                                                            'slug': self.object.slug,
                                                                            'window': 'window'})

            success_url = reverse_lazy('subjects:view',
                                       kwargs={'slug': self.object.topic.subject.slug})

        return success_url


class DeleteView(LoginRequiredMixin, generic.DeleteView):
    log_component = "resources"
    log_action = "delete"
    log_resource = "questionary"
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'resources/delete.html'
    model = Questionary
    context_object_name = 'resource'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        questionary = get_object_or_404(Questionary, slug=slug)

        if not has_subject_permissions(request.user, questionary.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request,
                         _('The questionary %s of the topic %s was removed successfully!') % (
                             self.object.name, self.object.topic.name))

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['questionary_id'] = self.object.id
        self.log_context['questionary_name'] = self.object.name
        self.log_context['questionary_slug'] = self.object.slug

        super(DeleteView, self).create_log(self.request.user, self.log_component, self.log_action,
                                           self.log_resource)

        return reverse_lazy('subjects:view', kwargs={'slug': self.object.topic.subject.slug})


def countQuestions(request):
    tags = request.GET.get('values', None)
    total = 0

    if tags:
        tags = tags.split(',')
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(DISTINCT question_id) FROM banco_questoes_question_categories AS a WHERE %s <@ (SELECT array_agg(CAST(tag_id as text)) FROM public.banco_questoes_question_categories AS c WHERE c.question_id = a.question_id)',
                [tags])
            total = cursor.fetchone()
            total = total[0]

    return JsonResponse({'total': total})


@log_decorator("resources", "answer", "questionary")
def answer(request):
    question = request.POST.get('question')
    answer = request.POST.get('answer')

    question = get_object_or_404(UserAnswer, id=question)
    answer = get_object_or_404(Alternative, id=answer)

    log_action = "finish"
    insert_log = False

    userquest = question.user_quest

    if not UserAnswer.objects.filter(user_quest=userquest, answer__isnull=False).exists():
        insert_log = True
        log_action = "start"

    question.answer = answer
    question.is_correct = answer.is_correct

    question.save()

    userquest.last_update = datetime.now()

    userquest.save()

    # add request context to log
    questionary_data = userquest.questionary
    request.log_context = {"question_id": userquest.questionary.id,
                           "is_correct": question.is_correct, "time_to_answer": (
                question.created_at - question.question.created_at).total_seconds(),
                           "subject_id": questionary_data.topic.subject.id,
                           "category_id": questionary_data.topic.subject.category.id,
                           "topic_id": questionary_data.topic.id,
                           "topic_slug": questionary_data.topic.slug,
                           "topic_name": questionary_data.topic.name}

    if not UserAnswer.objects.filter(user_quest=userquest,
                                     answer__isnull=True).exists() or insert_log:
        log = Log()
        log.user = str(request.user)
        log.user_id = request.user.id
        log.user_email = request.user.email
        log.component = "resources"
        log.action = log_action
        log.resource = "questionary"

        log.context = {"subject_id": questionary_data.topic.subject.id,
                       "category_id": questionary_data.topic.subject.category.id,
                       "topic_id": questionary_data.topic.id,
                       "topic_slug": questionary_data.topic.slug,
                       "topic_name": questionary_data.topic.name,
                       'questionary_id': questionary_data.id,
                       'questionary_name': questionary_data.name,
                       'questionary_slug': questionary_data.slug}
        log.save()

    return JsonResponse(
        {'last_update': formats.date_format(userquest.last_update, "SHORT_DATETIME_FORMAT"),
         'answered': userquest.useranswer_userquest.filter(answer__isnull=False).count()})


class StatisticsView(LoginRequiredMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view_statistics'
    log_resource = 'questionary'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Questionary
    template_name = 'questionary/relatorios.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        questionary = get_object_or_404(Questionary, slug=slug)

        if not has_subject_permissions(request.user, questionary.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(StatisticsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatisticsView, self).get_context_data(**kwargs)

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['questionary_id'] = self.object.id
        self.log_context['questionary_name'] = self.object.name
        self.log_context['questionary_slug'] = self.object.slug

        super(StatisticsView, self).create_log(self.request.user, self.log_component,
                                               self.log_action, self.log_resource)

        context['title'] = _('Questionary Reports')

        slug = self.kwargs.get('slug')
        questionary = get_object_or_404(Questionary, slug=slug)

        date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language',
                                                               '') == 'pt-br' else "%m/%d/%Y %I:%M %p"

        if self.request.GET.get('language', '') == "":
            start_date = datetime.now() - timedelta(30)
            end_date = datetime.now()
        else:
            start_date = datetime.strptime(self.request.GET.get('init_date', ''), date_format)
            end_date = datetime.strptime(self.request.GET.get('end_date', ''), date_format)

        context["init_date"] = start_date
        context["end_date"] = end_date

        alunos = questionary.students.all()

        if questionary.all_students:
            alunos = questionary.topic.subject.students.all()

        vis_ou = Log.objects.filter(context__contains={'questionary_id': questionary.id},
                                    resource="questionary",
                                    user_email__in=(aluno.email for aluno in alunos),
                                    datetime__range=(
                                        start_date, end_date + timedelta(minutes=1))).filter(
            Q(action="view") | Q(action="finish") | Q(action="start"))

        did, n_did, history = str(_("Realized")), str(_("Unrealized")), str(_("Historic"))
        re = []
        data_n_did, data_history = [], []
        json_n_did, json_history = {}, {}

        for log_al in vis_ou.order_by("datetime"):
            if log_al.action == 'view':
                if any(log_al.user in x for x in data_history):
                    continue
            elif log_al.action == 'finish':
                index = None

                for dh in data_history:
                    if log_al.user in dh:
                        index = dh
                        break

                if not index is None:
                    data_history.remove(index)

            data_history.append([log_al.user,
                                 ", ".join([str(x) for x in
                                            questionary.topic.subject.group_subject.filter(
                                                participants__email=log_al.user_email)]),
                                 log_al.action, log_al.datetime])

        json_history["data"] = data_history

        not_view = alunos.exclude(email__in=[log.user_email for log in
                                             vis_ou.filter(action="view").distinct("user_email")])
        index = 0
        for alun in not_view:
            data_n_did.append([index, str(alun), ", ".join([str(x) for x in
                                                            questionary.topic.subject.group_subject.filter(
                                                                participants__email=alun.email)]),
                               str(_('View')), str(alun.email)])
            index += 1

        not_start = alunos.exclude(email__in=[log.user_email for log in
                                              vis_ou.filter(action="start").distinct("user_email")])
        for alun in not_start:
            data_n_did.append([index, str(alun), ", ".join([str(x) for x in
                                                            questionary.topic.subject.group_subject.filter(
                                                                participants__email=alun.email)]),
                               str(_('Start')), str(alun.email)])
            index += 1

        not_finish = alunos.exclude(email__in=[log.user_email for log in
                                               vis_ou.filter(action="finish").distinct(
                                                   "user_email")])
        for alun in not_finish:
            data_n_did.append([index, str(alun), ", ".join([str(x) for x in
                                                            questionary.topic.subject.group_subject.filter(
                                                                participants__email=alun.email)]),
                               str(_('Finish')), str(alun.email)])
            index += 1

        json_n_did["data"] = data_n_did

        context["json_n_did"] = json_n_did
        context["json_history"] = json_history

        c_visualizou = vis_ou.filter(action="view").distinct("user_email").count()
        c_start = vis_ou.filter(action="start").distinct("user_email").count()
        c_finish = vis_ou.filter(action="finish").distinct("user_email").count()

        column_view = str(_('View'))
        column_start = str(_('Start'))
        column_finish = str(_('Finish'))

        re.append([str(_('Questionary')), did, n_did])
        re.append([column_view, c_visualizou, alunos.count() - c_visualizou])
        re.append([column_start, c_start, alunos.count() - c_start])
        re.append([column_finish, c_finish, alunos.count() - c_finish])

        context['topic'] = questionary.topic
        context['subject'] = questionary.topic.subject
        context['db_data'] = re
        context['title_chart'] = _('Actions about resource')
        context['title_vAxis'] = _('Quantity')
        context['view'] = column_view
        context['start'] = column_start
        context['finish'] = column_finish
        context["n_did_table"] = n_did
        context["did_table"] = did
        context["history_table"] = history

        return context


class SendMessage(LoginRequiredMixin, generic.edit.FormView):
    log_component = 'resources'
    log_action = 'send'
    log_resource = 'questionary'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'questionary/send_message.html'
    form_class = FormModalMessage

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        questionary = get_object_or_404(Questionary, slug=slug)
        self.questionary = questionary

        if not has_subject_permissions(request.user, questionary.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SendMessage, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        message = form.cleaned_data.get('comment')
        image = form.cleaned_data.get("image", '')
        users = (self.request.POST.get('users[]', '')).split(",")
        user = self.request.user
        subject = self.questionary.topic.subject

        channel_layer = get_channel_layer()

        if users[0] is not '':
            for u in users:
                to_user = User.objects.get(email=u)
                talk, create = Conversation.objects.get_or_create(user_one=user, user_two=to_user)
                created = TalkMessages.objects.create(text=message, talk=talk, user=user,
                                                      subject=subject, image=image)

                simple_notify = textwrap.shorten(strip_tags(message), width=30, placeholder="...")

                if image is not '':
                    simple_notify += " ".join(_("[Photo]"))

                notification = {
                    "type": "chat",
                    "subtype": "subject",
                    "space": subject.slug,
                    "user_icon": created.user.image_url,
                    "notify_title": str(created.user),
                    "simple_notify": simple_notify,
                    "view_url": reverse("chat:view_message", args=(created.id,), kwargs={}),
                    "complete": render_to_string("chat/_message.html", {"talk_msg": created},
                                                 self.request),
                    "container": "chat-" + str(created.user.id),
                    "last_date": _("Last message in %s") % (
                        formats.date_format(created.create_date, "SHORT_DATETIME_FORMAT"))
                }

                notification = json.dumps(notification)
                async_to_sync(channel_layer.send)("user-%s" % to_user.id, {'text': notification})

                ChatVisualizations.objects.create(viewed=False, message=created, user=to_user)

            success = str(_('The message was successfull sent!'))
            return JsonResponse({"message": success})

        erro = HttpResponse(str(_("No user selected!")))
        erro.status_code = 404
        return erro

    def get_context_data(self, **kwargs):
        context = super(SendMessage, self).get_context_data()
        context["questionary"] = get_object_or_404(Questionary, slug=self.kwargs.get('slug', ''))
        return context
