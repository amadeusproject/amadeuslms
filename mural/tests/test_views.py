""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase

from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

#Import factories
from categories.factories import RandomCategoryFactory
from subjects.factories import RandomSubjectFactory
from mural.factories import RandomGeneralPostFactory, RandomCategoryPostFactory, RandomSubjectPostFactory
from users.factories import RandomUserFactory

class TestViews(TestCase):
    staff = None

    professors = None
    students = None

    categories = None
    subjects = None
    topics = None
    generalPosts = None
    categoryPosts = None
    subjectPosts = None

    def setUp(self):
        self.create_users()
        self.create_categories()
        self.create_subjects()

    def create_users(self):
        self.staff = RandomUserFactory.create(is_staff=True)
        self.professors = RandomUserFactory.create_batch(3, is_staff=False)
        self.students = RandomUserFactory.create_batch(9, is_staff=False)

    def create_categories(self):
        self.categories = RandomCategoryFactory.create_batch(3)

    def create_subjects(self):
        self.subjects = RandomSubjectFactory.create_batch(5, category=self.categories[0], professor=(self.professors[0],), students=(self.students[0:2]))
        self.subjects += RandomSubjectFactory.create_batch(5, category=self.categories[1], professor=(self.professors[1],), students=(self.students[3:5]))
        self.subjects += RandomSubjectFactory.create_batch(5, category=self.categories[2], professor=(self.professors[2],), students=(self.students[6:8]))

    def create_posts(self):
        generalPosts = RandomGeneralPostFactory.create_batch(5, user=self.professors[0])
        generalPosts += RandomGeneralPostFactory.create_batch(5, user=self.students[5])

        categoryPosts = RandomCategoryPostFactory.create_batch(5, space=self.categories[1], user=self.professors[1])
        categoryPosts += RandomCategoryPostFactory.create_batch(5, space=self.categories[0], user=self.students[0])
        
        subjectPosts = RandomSubjectPostFactory.create_batch(5, space=self.subjects[12], user=self.professors[2])
        subjectPosts += RandomSubjectPostFactory.create_batch(5, space=self.subjects[6], user=self.students[3])

    def isListEqual(self, a, b):
        intersec = list(set(a).intersection(b))

        return len(intersec) == 0

    def test_general_index(self):
        self.client.force_login(self.professors[1])

        response = self.client.get(reverse("mural:manage_general"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/list.html")
