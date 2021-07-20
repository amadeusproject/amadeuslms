""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase

from django.utils.translation import ugettext_lazy as _

from datetime import datetime

from categories.models import Category
from subjects.models import Subject
from topics.models import Topic, Resource

from topics.forms import TopicForm

class TestForm(TestCase):
    subject = None

    def create_subject(self):
        if self.subject is None:
            category = Category.objects.create(name="Categoria Teste")
            self.subject = Subject.objects.create(name="Subject Teste", visible=True, init_date=datetime.now(), end_date=datetime.now(), subscribe_begin=datetime.now(), subscribe_end=datetime.now(), category=category)

    def create_topic(self):
        self.create_subject()
        
        return Topic.objects.create(name="Tópico Teste", repository=True, subject=self.subject)

    def test_form_subject_initial_value(self):
        self.create_subject()

        form = TopicForm(initial={"subject": self.subject})

        self.assertEquals(form.subject, self.subject)

    def test_form_repo_edit_name_readonly(self):
        topic = self.create_topic()

        form = TopicForm(instance=topic, initial={"subject": self.subject})

        self.assertTrue(form.fields["name"].widget.attrs['readonly'])

    def test_form_repository(self):
        self.create_subject()

        form_data = {"name": "topico 1", "repository": True}
        form = TopicForm(data=form_data, initial={"subject": self.subject})

        self.assertTrue(form.is_valid())

    def test_form_multiple_repos(self):
        topic = self.create_topic()

        form_data = {"name": "topico 1", "repository": True}
        form = TopicForm(data=form_data, initial={"subject": self.subject})

        self.assertEquals(form.errors["repository"], [_('This subject already has a repository')])
    
    def test_form_repo_edit_not_same_name(self):
        topic = self.create_topic()

        form_data = {"name": topic.name, "description": topic.description, "visible": topic.visible, "repository": topic.repository}
        form = TopicForm(instance=topic, data=form_data, initial={"subject": self.subject})
        
        self.assertTrue(form.is_valid())

    def test_form_same_name_repo(self):
        topic = self.create_topic()

        form_data = {"name": "Tópico Teste", "repository": True}
        form = TopicForm(data=form_data, initial={"subject": self.subject})

        self.assertEquals(form.errors["name"], [_('This subject already has a repository')])

    def test_form_same_name(self):
        topic = self.create_topic()

        form_data = {"name": "Tópico Teste", "repository": False}
        form = TopicForm(data=form_data, initial={"subject": self.subject})

        self.assertEquals(form.errors["name"], [_('This subject already has a topic with this name')])

