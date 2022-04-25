""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase

from django.utils.translation import ugettext_lazy as _

from datetime import datetime, timedelta

from categories.models import Category
from subjects.models import Subject, Tag
from users.models import User

from subjects.forms import SubjectForm

class TestForm(TestCase):
    category = None
    subject = None
    user = None

    def setUp(self):
        self.create_category()
        self.create_subject()
        self.create_user()

    def create_category(self):
        self.category = Category.objects.create(name="Categoria Teste")

    def create_subject(self):
        self.subject = Subject.objects.create(name="Subject Teste", visible=True, init_date=datetime.now(), end_date=datetime.now(), subscribe_begin=datetime.now(), subscribe_end=datetime.now(), category=self.category)
        self.subject.tags.add(Tag.objects.create(name="unit"))
        self.subject.tags.add(Tag.objects.create(name="assunto"))

    def create_user(self):
        self.user = User.objects.create(username = 'usuario', email = 'usuario@amadeus.br', password = 'amadeus')

    def test_form_category_initial_value(self):
        form = SubjectForm(initial={"category": self.category})

        self.assertEquals(form.category_id, self.category.id)

    def test_form_same_name(self):
        form_data = {
            "name": self.subject.name, 
            "visible": True, 
            "init_date": datetime.now(), 
            "end_date": datetime.now(), 
            "subscribe_begin": datetime.now(), 
            "subscribe_end": datetime.now(), 
            "category": self.category
        }

        form = SubjectForm(data=form_data, initial={"category": self.category})

        self.assertEquals(form.errors["name"], [_('There is another subject with this name, try another one.')])

    def test_form_subscribe_date_init(self):
        form_data = {
            "name": "Assunto 2", 
            "visible": True, 
            "init_date": datetime.now(), 
            "end_date": datetime.now(), 
            "subscribe_begin": datetime.now() - timedelta(days=1), 
            "subscribe_end": datetime.now(), 
            "category": self.category
        }

        form = SubjectForm(data=form_data, initial={"category": self.category})

        self.assertEquals(form.errors["subscribe_begin"], [_('This date must be today or after')])

    def test_form_subscribe_date_end(self):
        form_data = {
            "name": "Assunto 2", 
            "visible": True, 
            "init_date": datetime.now(), 
            "end_date": datetime.now(), 
            "subscribe_begin": datetime.now(), 
            "subscribe_end": datetime.now() - timedelta(days=1), 
            "category": self.category
        }

        form = SubjectForm(data=form_data, initial={"category": self.category})

        self.assertEquals(form.errors["subscribe_end"], [_('This date must be equal subscribe begin or after')])

    def test_form_init_date(self):
        form_data = {
            "name": "Assunto 2", 
            "visible": True, 
            "init_date": datetime.now(), 
            "end_date": datetime.now(), 
            "subscribe_begin": datetime.now(), 
            "subscribe_end": datetime.now() + timedelta(days=1), 
            "category": self.category
        }

        form = SubjectForm(data=form_data, initial={"category": self.category})

        self.assertEquals(form.errors["init_date"], [_('This date must be after subscribe end')])

    def test_form_end_date(self):
        form_data = {
            "name": "Assunto 2", 
            "visible": True, 
            "init_date": datetime.now() + timedelta(days=2), 
            "end_date": datetime.now() + timedelta(days=1), 
            "subscribe_begin": datetime.now(), 
            "subscribe_end": datetime.now() + timedelta(days=1), 
            "category": self.category
        }

        form = SubjectForm(data=form_data, initial={"category": self.category})

        self.assertEquals(form.errors["end_date"], [_('This date must be equal init date or after')])

    def test_form_tags(self):
        form_data = {
            "name": "Assunto 2", 
            "visible": True, 
            "init_date": datetime.now() + timedelta(days=2), 
            "end_date": datetime.now() + timedelta(days=3), 
            "subscribe_begin": datetime.now(), 
            "subscribe_end": datetime.now() + timedelta(days=1), 
            "category": self.category,
            "tags": "teste,test,testando"
        }

        form = SubjectForm(data=form_data, initial={"category": self.category})
        form.save()

        subject = Subject.objects.latest("id")

        tags = [str(t) for t in subject.tags.all()]

        self.assertIn("teste", tags)
        self.assertIn("test", tags)
        self.assertIn("testando", tags)

    def test_form_update_tags(self):
        form_data = {
            "name": self.subject.name, 
            "visible": True, 
            "init_date": datetime.now() + timedelta(days=2), 
            "end_date": datetime.now() + timedelta(days=3), 
            "subscribe_begin": datetime.now(), 
            "subscribe_end": datetime.now() + timedelta(days=1), 
            "category": self.category,
            "tags": "unit,test,testando"
        }

        form = SubjectForm(instance=self.subject, data=form_data)
        form.save()

        subject = Subject.objects.get(id=self.subject.id)

        tags = [str(t) for t in subject.tags.all()]

        self.assertNotIn("assunto", tags)
        self.assertIn("unit", tags)
        self.assertIn("test", tags)
        self.assertIn("testando", tags)

    def test_form_participants_field(self):
        form_data = {
            "name": "Assunto 2", 
            "visible": True, 
            "init_date": datetime.now() + timedelta(days=2), 
            "end_date": datetime.now() + timedelta(days=3), 
            "subscribe_begin": datetime.now(), 
            "subscribe_end": datetime.now() + timedelta(days=1), 
            "category": self.category,
            "tags": "teste,test,testando"
        }

        form = SubjectForm(data=form_data, initial={"category": self.category})

        participants = [c[1] for c in form.fields["students"].choices]

        self.assertIn("%s - (%s)"%(str(self.user), self.user.email), participants)