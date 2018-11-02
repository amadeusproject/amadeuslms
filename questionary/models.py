""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import os
from django.db import models
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from banco_questoes.models import Question, Alternative
from subjects.models import Tag
from topics.models import Resource
from users.models import User

class Questionary(Resource):
    presentation = models.TextField(_('Presentation'), blank = True)
    data_ini = models.DateTimeField(_('Init Date'), auto_now_add = False)
    data_end = models.DateTimeField(_('End Date'), auto_now_add = False)

    class Meta:
        verbose_name = "Questionary"
        verbose_name_plural = "Questionaries"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.name

    def access_link(self):
        return reverse_lazy('questionary:view', args = (), kwargs = {'slug': self.slug})

    def update_link(self):
        return 'questionary:update'

    def delete_link(self):
        return 'questionary:delete'

    def delete_message(self):
        return _('Are you sure you want delete the Questionary')

    def get_data_ini(self):
        return self.data_ini
    
    def get_data_end(self):
        return self.data_end

class Specification(models.Model):
    questionary = models.ForeignKey(Questionary, verbose_name = _('Questionary'), related_name = 'spec_questionary', null = True)
    categories = models.ManyToManyField(Tag, verbose_name = 'categories', related_name = 'questionary_categories', blank = False)
    n_questions = models.PositiveSmallIntegerField(_('Number of Questions'), null = True)

class UserQuest(models.Model):
    questionary = models.ForeignKey(Questionary, verbose_name = _('Questionary'), related_name = 'userquest_questionary', null = True)
    student = models.ForeignKey(User, verbose_name = _('User'), related_name = 'userquest_user', null = True)
    data_ini = models.DateTimeField(_('Init Date'), auto_now_add = True)
    last_update = models.DateTimeField(_('Last update'), auto_now_add = True)

class UserAnswer(models.Model):
    user_quest = models.ForeignKey(UserQuest, verbose_name = _('User Questionary'), related_name = 'useranswer_userquest', null = True)
    question = models.ForeignKey(Question, verbose_name = _('Question'), related_name = 'useranswer_question', null = True)
    answer = models.ForeignKey(Alternative, verbose_name = _('Answer'), related_name = 'useranswer_alternative', null = True)
    is_correct = models.BooleanField(_('Is correct?'), default = False)
    order = models.PositiveSmallIntegerField(_('Order'), null = True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add = True)