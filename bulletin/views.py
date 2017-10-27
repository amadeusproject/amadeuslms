""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from amadeus.permissions import has_subject_permissions, has_resource_permissions
from .utils import brodcast_dificulties
from goals.models import Goals,GoalItem,MyGoals

import xlwt
import xlrd
import time
import datetime
from statistics import median
from log.mixins import LogMixin

from topics.models import Topic

from django.conf import settings
import os
from os.path import join
from django.utils import timezone

from pendencies.forms import PendenciesForm

from .forms import BulletinForm
from .models import Bulletin, valid_formats

from log.models import Log
from log.decorators import log_decorator

from chat.models import Conversation, TalkMessages, ChatVisualizations
from users.models import User
from subjects.models import Subject

from .forms import FormModalMessage

from django.template.loader import render_to_string
from django.utils import formats
import textwrap
from django.utils.html import strip_tags
import json
from channels import Group

class NewWindowView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/window_view.html'
    model = Bulletin
    context_object_name = 'bulletin'
    student = None

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug=slug)

        if not has_resource_permissions(request.user, bulletin):
            return redirect(reverse_lazy('subjects:home'))

        return super(NewWindowView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        difficulties = self.request.POST.get('difficulties', None)
        user_selected = request.POST.get('selected_student', None)

        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug=slug)

        self.object = bulletin

        if has_subject_permissions(request.user, bulletin.topic.subject):
            if not user_selected is None:
                user = User.objects.get(email = user_selected)
                self.student = user
        else:
            if not difficulties is None and not difficulties == "":
                print(difficulties)
                message = _("#Difficulty(ies) found in %s")%(str(bulletin)) + ":<p>" + difficulties + "</p>"

                brodcast_dificulties(self.request, message, bulletin.topic.subject)

                self.log_context = {}
                self.log_context['category_id'] = bulletin.topic.subject.category.id
                self.log_context['category_name'] = bulletin.topic.subject.category.name
                self.log_context['category_slug'] = bulletin.topic.subject.category.slug
                self.log_context['subject_id'] = bulletin.topic.subject.id
                self.log_context['subject_name'] = bulletin.topic.subject.name
                self.log_context['subject_slug'] = bulletin.topic.subject.slug
                self.log_context['topic_id'] = bulletin.topic.id
                self.log_context['topic_name'] = bulletin.topic.name
                self.log_context['topic_slug'] = bulletin.topic.slug
                self.log_context['bulletin_id'] = bulletin.id
                self.log_context['bulletin_name'] = bulletin.name
                self.log_context['bulletin_slug'] = bulletin.slug

                self.log_action = "send_difficulties"

                super(NewWindowView, self).createLog(self.request.user, self.log_component, self.log_action,
                                             self.log_resource, self.log_context)

                self.log_action = "view"
                self.log_context = {}

                messages.success(self.request, message = _("Difficulties sent to the subject professor(s)"))

                return self.render_to_response(context = self.get_context_data())
            else:
                messages.error(self.request, message = _("You should inform some difficulty"))
                return self.render_to_response(context = self.get_context_data())

        return self.render_to_response(context = self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(NewWindowView, self).get_context_data(**kwargs)
        context['title'] = self.object.name

        context['topic'] = self.object.topic
        context['subject'] = self.object.topic.subject


        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug
        self.log_context['timestamp_start'] = str(int(time.time()))

        super(NewWindowView, self).createLog(self.request.user, self.log_component, self.log_action,
                                             self.log_resource, self.log_context)

        self.request.session['log_id'] = Log.objects.latest('id').id

        topic = self.object.topic

        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug=slug)
        students = User.objects.filter(subject_student = bulletin.topic.subject).order_by('social_name', 'username')

        if has_subject_permissions(self.request.user, bulletin.topic.subject):
            if  not self.student is None:
                estudante = self.student
            else:
                estudante = students.first()
        else:
            estudante = self.request.user

        meta_geral = Goals.objects.get(topic=topic)
        metas = GoalItem.objects.filter(goal = meta_geral)
        metas_pessoais = []
        n_submeteu = False
        for m in metas:
            if MyGoals.objects.filter(item = m, user = estudante).exists():
                metas_pessoais.append(MyGoals.objects.get(item = m, user = estudante))
                n_submeteu = False
            else:
                n_submeteu = True

        itens_da_meta = sorted(list(metas), key = lambda met: met.id)
        metas_pessoais = sorted(list(metas_pessoais), key = lambda me: me.id)
        lista_metas = [{'description':geral.description, 'desejada':geral.ref_value} for geral in itens_da_meta ]

        for x in range(len(lista_metas)):
            if n_submeteu:
                lista_metas[x]['estabelecida'] = lista_metas[x]['desejada']
            else:
                lista_metas[x]['estabelecida'] = metas_pessoais[x].value

        alcancadas, medias = read_excel_file(estudante,meta_geral,len(itens_da_meta),bulletin)
        maximos, medianas, resultados,titulos = read_excel_file_indicators(estudante,bulletin)

        for x in range(len(lista_metas)):
            lista_metas[x]['alcancada'] = alcancadas[x]
            lista_metas[x]['media'] = medias[x]

        qtd_atendida = 0
        qtd_metas = len(itens_da_meta)
        for x in range(len(lista_metas)):
            #Caso 1: Meta alcançada foi maior que a meta desejada
            caso1 = lista_metas[x]['alcancada'] > lista_metas[x]['desejada']

            #Caso 2: Meta alcançada foi maior que a meta estabelecida
            caso2 = lista_metas[x]['alcancada'] > lista_metas[x]['estabelecida']
            if caso1 or caso2:
                qtd_atendida += 1

        porcentagem = calcula_porcentagem(qtd_atendida,qtd_metas)

        #Adicionando ao contexto
        context['metas'] = lista_metas
        context['percent'] = porcentagem
        context['maximos'] = maximos
        context['medianas'] = medianas
        context['resultados'] = resultados
        context['titulos'] = titulos
        context['student'] = self.request.POST.get('selected_student', students.first().email)
        context['students'] = students
        
        return context

class InsideView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/view.html'
    model = Bulletin
    context_object_name = 'bulletin'
    student = None

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug=slug)

        if not has_resource_permissions(request.user, bulletin):
            return redirect(reverse_lazy('subjects:home'))

        return super(InsideView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        difficulties = self.request.POST.get('difficulties', None)
        user_selected = request.POST.get('selected_student', None)

        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug=slug)

        self.object = bulletin

        if has_subject_permissions(request.user, bulletin.topic.subject):
            if not user_selected is None:
                user = User.objects.get(email = user_selected)
                self.student = user
        else:
            if not difficulties is None and not difficulties == "":
                message = _("#Dificulty(ies) found in %s")%(str(bulletin)) + ":<p>" + difficulties + "</p>"

                brodcast_dificulties(self.request, message, bulletin.topic.subject)

                self.log_context = {}
                self.log_context['category_id'] = bulletin.topic.subject.category.id
                self.log_context['category_name'] = bulletin.topic.subject.category.name
                self.log_context['category_slug'] = bulletin.topic.subject.category.slug
                self.log_context['subject_id'] = bulletin.topic.subject.id
                self.log_context['subject_name'] = bulletin.topic.subject.name
                self.log_context['subject_slug'] = bulletin.topic.subject.slug
                self.log_context['topic_id'] = bulletin.topic.id
                self.log_context['topic_name'] = bulletin.topic.name
                self.log_context['topic_slug'] = bulletin.topic.slug
                self.log_context['bulletin_id'] = bulletin.id
                self.log_context['bulletin_name'] = bulletin.name
                self.log_context['bulletin_slug'] = bulletin.slug

                self.log_action = "send_difficulties"

                super(InsideView, self).createLog(self.request.user, self.log_component, self.log_action,
                                             self.log_resource, self.log_context)

                self.log_action = "view"
                self.log_context = {}

                messages.success(self.request, message = _("Difficulties sent to the subject professor(s)"))
                return self.render_to_response(context = self.get_context_data())
            else:
                messages.error(self.request, message = _("You should inform some difficulty"))
                return self.render_to_response(context = self.get_context_data())

        return self.render_to_response(context = self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(InsideView, self).get_context_data(**kwargs)

        context['title'] = self.object.name

        context['topic'] = self.object.topic
        context['subject'] = self.object.topic.subject

        self.log_context['category_id'] = self.object.topic.subject.category.id
        self.log_context['category_name'] = self.object.topic.subject.category.name
        self.log_context['category_slug'] = self.object.topic.subject.category.slug
        self.log_context['subject_id'] = self.object.topic.subject.id
        self.log_context['subject_name'] = self.object.topic.subject.name
        self.log_context['subject_slug'] = self.object.topic.subject.slug
        self.log_context['topic_id'] = self.object.topic.id
        self.log_context['topic_name'] = self.object.topic.name
        self.log_context['topic_slug'] = self.object.topic.slug
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug
        self.log_context['timestamp_start'] = str(int(time.time()))

        super(InsideView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        self.request.session['log_id'] = Log.objects.latest('id').id


        topic = self.object.topic
        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug=slug)
        students = User.objects.filter(subject_student = bulletin.topic.subject).order_by('social_name', 'username')
        if has_subject_permissions(self.request.user, bulletin.topic.subject):
            if  not self.student is None:
                estudante = self.student
            else:
                estudante = students.first()
        else:
            estudante = self.request.user

        meta_geral = Goals.objects.get(topic=topic)
        metas = GoalItem.objects.filter(goal = meta_geral)
        metas_pessoais = []
        n_submeteu = False
        for m in metas:
            if MyGoals.objects.filter(item = m, user = estudante).exists():
                metas_pessoais.append(MyGoals.objects.get(item = m, user = estudante))
                n_submeteu = False
            else:
                n_submeteu = True

        itens_da_meta = sorted(list(metas), key = lambda met: met.id)
        metas_pessoais = sorted(list(metas_pessoais), key = lambda me: me.id)
        lista_metas = [{'description':geral.description, 'desejada':geral.ref_value} for geral in itens_da_meta ]

        for x in range(len(lista_metas)):
            if n_submeteu:
                lista_metas[x]['estabelecida'] = lista_metas[x]['desejada']
            else:
                lista_metas[x]['estabelecida'] = metas_pessoais[x].value

        alcancadas, medias = read_excel_file(estudante,meta_geral,len(itens_da_meta),bulletin)
        maximos, medianas, resultados,titulos = read_excel_file_indicators(estudante,bulletin)

        for x in range(len(lista_metas)):
            lista_metas[x]['alcancada'] = alcancadas[x]
            lista_metas[x]['media'] = medias[x]


        qtd_atendida = 0
        qtd_metas = len(itens_da_meta)
        for x in range(len(lista_metas)):
            #Caso 1: Meta alcançada foi maior que a meta desejada
            caso1 = lista_metas[x]['alcancada'] > lista_metas[x]['desejada']

            #Caso 2: Meta alcançada foi maior que a meta estabelecida
            caso2 = lista_metas[x]['alcancada'] > lista_metas[x]['estabelecida']
            if caso1 or caso2:
                qtd_atendida += 1

        porcentagem = calcula_porcentagem(qtd_atendida,qtd_metas)

        #Adicionando ao contexto
        context['metas'] = lista_metas
        context['percent'] = porcentagem
        context['maximos'] = maximos
        context['medianas'] = medianas
        context['resultados'] = resultados
        context['titulos'] = titulos
        context['student'] = self.request.POST.get('selected_student', students.first().email)
        context['students'] = students
        return context

class CreateView(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
    log_component = 'resources'
    log_action = 'create'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/create.html'
    form_class = BulletinForm

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        existe_meta = Goals.objects.filter(topic=topic).exists()
        existe_boletim = Bulletin.objects.filter(topic=topic).exists()

        if not existe_meta:
            messages.error(request,_("The topic %s has no goals, so you can't create a Bulletin.") %(topic) )
            caminho1 = request.META['HTTP_REFERER']
            return redirect(caminho1)

        if existe_meta:
            meta_geral = Goals.objects.get(topic=topic)
            if meta_geral.limit_submission_date.date() > datetime.datetime.today().date():
                messages.error(request,_("The deadline to submit the goals of the topic %s has not yet closed, so you can't create a Bulletin.") %(topic) )
                caminho2 = request.META['HTTP_REFERER']
                return redirect(caminho2)

        if existe_boletim:
            messages.error(request,_("The topic %s already has a Bulletin, so you can't create another.") %(topic) )
            caminho3 = request.META['HTTP_REFERER']
            return redirect(caminho3)

        if not has_subject_permissions(request.user, topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(CreateView, self).dispatch(request, *args, **kwargs)

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
        initial = super(CreateView, self).get_initial()

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
        self.object.all_students = True

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
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug

        super(CreateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)

        context['title'] = _('Create Bulletin')

        slug = self.kwargs.get('slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject


        meta_geral = Goals.objects.get(topic=topic)
        metas = GoalItem.objects.filter(goal = meta_geral)
        itens_da_meta = sorted(list(metas), key = lambda met: met.id)
        alunos =  sorted(list(meta_geral.topic.subject.students.all()), key = lambda e: e.id)
        create_excel_file(alunos, itens_da_meta,meta_geral)
        context['goal_file'] = str(meta_geral.slug)
        context['mimeTypes'] = valid_formats


        return context

    def get_success_url(self):
        messages.success(self.request, _('The Bulletin "%s" was added to the Topic "%s" of the virtual environment "%s" successfully!')%(self.object.name, self.object.topic.name, self.object.topic.subject.name))

        success_url = reverse_lazy('bulletin:view', kwargs = {'slug': self.object.slug})

        if self.object.show_window:
            self.request.session['resources'] = {}
            self.request.session['resources']['new_page'] = True
            self.request.session['resources']['new_page_url'] = reverse('bulletin:window_view', kwargs = {'slug': self.object.slug})

            success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

        return success_url

def download_excel(request, file):
    filepath = os.path.join('bulletin', os.path.join('sheets', os.path.join('xls', file + '.xls')))

    if not os.path.exists(filepath):
        raise Http404()

    response = HttpResponse(open(filepath, 'rb').read())
    response['Content-Type'] = 'application/force-download'
    response['Pragma'] = 'public'
    response['Expires'] = '0'
    response['Cache-Control'] = 'must-revalidate, post-check=0, pre-check=0'
    response['Content-Disposition'] = 'attachment; filename=%s' % (file + '.xls')
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Length'] = str(os.path.getsize(filepath))

    return response

def create_excel_file(estudantes,metas,meta):
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u'Bulletin')
    worksheet.write(0, 0, u'ID do Usuário')
    worksheet.write(0, 1, u'Usuário')
    count_meta = 2
    contador_estudante = 1

    for m in metas:
        worksheet.write(0,count_meta,u'%s' % (m.description) )
        count_meta += 1

    for estudante in estudantes:
        worksheet.write(contador_estudante,0,estudante.id )

        nome = str(estudante)
        worksheet.write(contador_estudante,1,nome)

        contador_estudante += 1

    path1 = os.path.join(settings.BASE_DIR,'bulletin')
    path2 = os.path.join(path1,'sheets')
    path3 = os.path.join(path2,'xls')

    nome = str(meta.slug) + ".xls"
    folder_path = join(path3, nome)

    #check if the folder already exists
    if not os.path.isdir(path3):
        os.makedirs(path3)

    workbook.save(folder_path)

def read_excel_file(estudante,meta,qtd,boletim):
    nome = boletim.file_content.path
    arquivo = xlrd.open_workbook(nome)
    planilha = arquivo.sheet_by_index(0)
    alcance = []
    medias = []
    soma = 0

    for n in range(planilha.nrows):
        if n == 0:
            continue
        else:
            linha = planilha.row_values(n)
            if int(linha[0]) == int(estudante.id):
                for x in range(2,2+qtd):
                    alcance.append(int(linha[x]))
                break
    if len(alcance) == 0:
        for x in range(0,qtd):
            alcance.append(0)

    for b in range(2,planilha.ncols):
        soma = int(sum(list(planilha.col_values(b,1,planilha.nrows))))
        media = soma // (planilha.nrows - 1)
        medias.append(media)

    if len(medias) == 0:
        for x in range(0,qtd):
            medias.append(0)

    return alcance, medias

def read_excel_file_indicators(estudante,boletim):
    name = boletim.indicators.path
    arq = xlrd.open_workbook(name)
    sheet = arq.sheet_by_index(0)
    maximos = []
    medianas = []
    resultados = []
    ind1 = []
    ind2 = []
    ind3 = []
    ind4 = []
    ind5 = []
    ind6 = []

    #Adicionando na lista de cada indicador o resultado de cada estudante
    for n in range(0,sheet.nrows):
        if n == 0:
            linha = sheet.row_values(n,2,8)
            titulos = list(linha)

        else:
            linha = sheet.row_values(n)
            if int(linha[8]) == 1:
                ind1.append(int(linha[2]))
                ind2.append(int(linha[3]))
                ind3.append(int(linha[4]))
                ind4.append(int(linha[5]))
                ind5.append(int(linha[6]))
                ind6.append(int(linha[7]))
            if int(linha[0]) == int(estudante.id):
                for x in range(2,8):
                    resultados.append(int(linha[x]))

    #Adicionando na lista de maximos o valor máximo para cada indicador
    maximos.append(max(ind1))
    maximos.append(max(ind2))
    maximos.append(max(ind3))
    maximos.append(max(ind4))
    maximos.append(max(ind5))
    maximos.append(max(ind6))

    #Adicionando na lista de medianas o valor da mediana para cada indicador
    mediana1, mediana2, mediana3, mediana4, mediana5, mediana6 = round(median(ind1), 1), round(median(ind2), 1), round(median(ind3), 1), round(median(ind4), 1), round(median(ind5), 1), round(median(ind6), 1)

    medianas.append(mediana1)
    medianas.append(mediana2)
    medianas.append(mediana3)
    medianas.append(mediana4)
    medianas.append(mediana5)
    medianas.append(mediana6)

    #Checando caso quem está visualizando não seja um estudante, dai preenche com 0
    if len(resultados) == 0:
        resultados = [0] * 6

    return maximos, medianas, resultados, titulos

def calcula_porcentagem(parte, todo):
  return int(100 * int(parte)/int(todo))

class UpdateView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    log_component = 'resources'
    log_action = 'update'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/update.html'
    model = Bulletin
    form_class = BulletinForm

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
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug

        super(UpdateView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        context['title'] = _('Update Bulletin')

        slug = self.kwargs.get('topic_slug', '')
        topic = get_object_or_404(Topic, slug = slug)

        context['topic'] = topic
        context['subject'] = topic.subject

        meta_geral = Goals.objects.get(topic=topic)
        metas = GoalItem.objects.filter(goal = meta_geral)
        itens_da_meta = sorted(list(metas), key = lambda met: met.id)
        alunos =  sorted(list(meta_geral.topic.subject.students.all()), key = lambda e: e.id)
        create_excel_file(alunos, itens_da_meta,meta_geral)
        context['goal_file'] = str(meta_geral.slug)
        context['mimeTypes'] = valid_formats
        context['resource'] = get_object_or_404(Bulletin, slug = self.kwargs.get('slug', ''))

        return context

    def get_success_url(self):
        messages.success(self.request, _('The Bulletin "%s" was updated successfully!')%(self.object.name))

        success_url = reverse_lazy('bulletin:view', kwargs = {'slug': self.object.slug})

        if self.object.show_window:
            self.request.session['resources'] = {}
            self.request.session['resources']['new_page'] = True
            self.request.session['resources']['new_page_url'] = reverse('bulletin:window_view', kwargs = {'slug': self.object.slug})

            success_url = reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})

        return success_url

class DeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
	log_component = 'resources'
	log_action = 'delete'
	log_resource = 'bulletin'
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'resources/delete.html'
	model = Bulletin
	context_object_name = 'resource'

	def dispatch(self, request, *args, **kwargs):
		slug = self.kwargs.get('slug', '')
		bulletin = get_object_or_404(Bulletin, slug = slug)

		if not has_subject_permissions(request.user, bulletin.topic.subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(DeleteView, self).dispatch(request, *args, **kwargs)

	def get_success_url(self):
		messages.success(self.request, _('The bulletin "%s" was removed successfully from virtual environment "%s"!')%(self.object.name, self.object.topic.subject.name))

		self.log_context['category_id'] = self.object.topic.subject.category.id
		self.log_context['category_name'] = self.object.topic.subject.category.name
		self.log_context['category_slug'] = self.object.topic.subject.category.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['bulletin_id'] = self.object.id
		self.log_context['bulletin_name'] = self.object.name
		self.log_context['bulletin_slug'] = self.object.slug

		super(DeleteView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('subjects:view', kwargs = {'slug': self.object.topic.subject.slug})


class StatisticsView(LoginRequiredMixin, LogMixin, generic.DetailView):
    log_component = 'resources'
    log_action = 'view_statistics'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Bulletin
    template_name = 'bulletin/relatorios.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug = slug)

        if not has_subject_permissions(request.user, bulletin.topic.subject):
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
        self.log_context['bulletin_id'] = self.object.id
        self.log_context['bulletin_name'] = self.object.name
        self.log_context['bulletin_slug'] = self.object.slug

        super(StatisticsView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)


        context['title'] = _('Bulletin Reports')

        slug = self.kwargs.get('slug')
        bulletin = get_object_or_404(Bulletin, slug = slug)

        date_format = "%d/%m/%Y %H:%M" if self.request.GET.get('language','') == 'pt-br' else "%m/%d/%Y %I:%M %p"
        if self.request.GET.get('language','') == "":
            start_date = datetime.datetime.now() - datetime.timedelta(30)
            end_date = datetime.datetime.now()
        else :
            start_date = datetime.datetime.strptime(self.request.GET.get('init_date',''),date_format)
            end_date = datetime.datetime.strptime(self.request.GET.get('end_date',''),date_format)
        context["init_date"] = start_date
        context["end_date"] = end_date
        alunos = bulletin.students.all()
        if bulletin.all_students :
        	alunos = bulletin.topic.subject.students.all()

        vis_ou = Log.objects.filter(context__contains={'bulletin_id':bulletin.id},resource="bulletin",action="view",user_email__in=(aluno.email for aluno in alunos), datetime__range=(start_date,end_date + datetime.timedelta(minutes = 1)))
        did,n_did,history = str(_("Realized")),str(_("Unrealized")),str(_("Historic"))
        re = []
        data_n_did,data_history = [],[]
        json_n_did, json_history = {},{}

        for log_al in vis_ou.order_by("datetime"):
            data_history.append([str(alunos.get(email=log_al.user_email)),
            ", ".join([str(x) for x in bulletin.topic.subject.group_subject.filter(participants__email=log_al.user_email)]),
            log_al.action,log_al.datetime])

        json_history["data"] = data_history

        not_view = alunos.exclude(email__in=[log.user_email for log in vis_ou.distinct("user_email")])
        index = 0
        for alun in not_view:
            data_n_did.append([index,str(alun),", ".join([str(x) for x in bulletin.topic.subject.group_subject.filter(participants__email=alun.email)]),str(_('View')), str(alun.email)])
            index += 1
        json_n_did["data"] = data_n_did


        context["json_n_did"] = json_n_did
        context["json_history"] = json_history
        c_visualizou = vis_ou.distinct("user_email").count()
        column_view = str(_('View'))
        re.append([str(_('Bulletin')),did,n_did])
        re.append([column_view,c_visualizou, alunos.count() - c_visualizou])
        context['topic'] = bulletin.topic
        context['subject'] = bulletin.topic.subject
        context['db_data'] = re
        context['title_chart'] = _('Actions about resource')
        context['title_vAxis'] = _('Quantity')
        context['view'] = column_view
        context["n_did_table"] = n_did
        context["did_table"] = did
        context["history_table"] = history
        return context

@log_decorator('resources', 'access_difficulties_modal', 'bulletin')
def bulletin_diff_view_log(request, slug):
    bulletin = get_object_or_404(Bulletin, slug = slug)

    log_context = {}
    log_context['category_id'] = bulletin.topic.subject.category.id
    log_context['category_name'] = bulletin.topic.subject.category.name
    log_context['category_slug'] = bulletin.topic.subject.category.slug
    log_context['subject_id'] = bulletin.topic.subject.id
    log_context['subject_name'] = bulletin.topic.subject.name
    log_context['subject_slug'] = bulletin.topic.subject.slug
    log_context['topic_id'] = bulletin.topic.id
    log_context['topic_name'] = bulletin.topic.name
    log_context['topic_slug'] = bulletin.topic.slug
    log_context['bulletin_id'] = bulletin.id
    log_context['bulletin_name'] = bulletin.name
    log_context['bulletin_slug'] = bulletin.slug

    request.log_context = log_context

    return JsonResponse({'message': 'ok'})

from django.http import HttpResponse #used to send HTTP 404 error to ajax

class SendMessage(LoginRequiredMixin, LogMixin, generic.edit.FormView):
    log_component = 'resources'
    log_action = 'send'
    log_resource = 'bulletin'
    log_context = {}

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'bulletin/send_message.html'
    form_class = FormModalMessage

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        bulletin = get_object_or_404(Bulletin, slug = slug)
        self.bulletin = bulletin

        if not has_subject_permissions(request.user, bulletin.topic.subject):
            return redirect(reverse_lazy('subjects:home'))

        return super(SendMessage, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        message = form.cleaned_data.get('comment')
        image = form.cleaned_data.get("image")
        users = (self.request.POST.get('users[]','')).split(",")
        user = self.request.user
        subject = self.bulletin.topic.subject

        if (users[0] is not ''):
            for u in users:
                to_user = User.objects.get(email=u)
                talk, create = Conversation.objects.get_or_create(user_one=user,user_two=to_user)
                created = TalkMessages.objects.create(text=message,talk=talk,user=user,subject=subject,image=image)

                simple_notify = textwrap.shorten(strip_tags(message), width = 30, placeholder = "...")

                if image is not '':
                    simple_notify += " ".join(_("[Photo]"))

                notification = {
                    "type": "chat",
                    "subtype": "subject",
                    "space": subject.slug,
                    "user_icon": created.user.image_url,
                    "notify_title": str(created.user),
                    "simple_notify": simple_notify,
                    "view_url": reverse("chat:view_message", args = (created.id, ), kwargs = {}),
                    "complete": render_to_string("chat/_message.html", {"talk_msg": created}, self.request),
                    "container": "chat-" + str(created.user.id),
                    "last_date": _("Last message in %s")%(formats.date_format(created.create_date, "SHORT_DATETIME_FORMAT"))
                }

                notification = json.dumps(notification)

                Group("user-%s" % to_user.id).send({'text': notification})

                ChatVisualizations.objects.create(viewed = False, message = created, user = to_user)

            success = str(_('The message was successfull sent!'))
            return JsonResponse({"message":success})
        erro = HttpResponse(str(_("No user selected!")))
        erro.status_code = 404
        return erro

    def get_context_data(self, **kwargs):
        context = super(SendMessage,self).get_context_data()
        context["bulletin"] = get_object_or_404(Bulletin, slug=self.kwargs.get('slug', ''))
        return context
