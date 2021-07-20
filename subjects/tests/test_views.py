""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from categories.models import Category
from subjects.models import Subject
from topics.models import Topic
from users.models import User
from log.models import Log

#Import factories
from categories.factories import RandomCategoryFactory
from subjects.factories import RandomSubjectFactory
from topics.factories import RandomTopicFactory
from users.factories import RandomUserFactory

class TestViews(TestCase):
    staff = None

    professors = None
    students = None

    categories = None
    subjects = None

    def setUp(self):
        self.create_users()
        self.create_categories()
        self.create_subjects()

    def create_users(self):
        self.staff = RandomUserFactory.create(is_staff=True)
        self.professors = RandomUserFactory.create_batch(3, is_staff=False)
        self.students = RandomUserFactory.create_batch(18, is_staff=False)

    def create_categories(self):
        self.categories = RandomCategoryFactory.create_batch(3)

    def create_subjects(self):
        self.subjects = RandomSubjectFactory.create_batch(5, category=self.categories[0], professor=(self.professors[0],), students=(self.students[0:5]))
        self.subjects += RandomSubjectFactory.create_batch(5, category=self.categories[1], professor=(self.professors[1],), students=(self.students[6:11]))
        self.subjects += RandomSubjectFactory.create_batch(5, category=self.categories[2], professor=(self.professors[2],), students=(self.students[12:17]))

    def test_subject_create_get_404(self):
        response = self.client.get(reverse("subjects:create", kwargs={"slug": "subject_teste"}))

        self.assertEquals(response.status_code, 404)