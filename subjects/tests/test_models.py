""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase

from datetime import datetime

from categories.models import Category
from subjects.models import Subject
from users.models import User

class TestModels(TestCase):
    subject = None

    def setUp(self):
        self.create_user()
        self.create_subject()

    def create_subject(self):
        category = Category.objects.create(name="Categoria Teste")
        self.subject = Subject.objects.create(name="Subject Teste", visible=True, init_date=datetime.now(), end_date=datetime.now(), subscribe_begin=datetime.now(), subscribe_end=datetime.now(), category=category)
        self.subject.students.add(self.user)

    def create_user(self):
        self.user = User.objects.create(username = 'usuario', email = 'usuario@amadeus.br', password = 'amadeus')

    def test_str(self):
        self.assertEquals(str(self.subject), self.subject.name)

    def test_participants(self):
        participants = self.subject.get_participants()

        self.assertIn(self.user, participants)