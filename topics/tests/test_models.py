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
from topics.models import Topic, Resource

class TestModels(TestCase):
    def create_topic(self):
        category = Category.objects.create(name="Categoria Teste")
        subject = Subject.objects.create(name="Subject Teste", visible=True, init_date=datetime.now(), end_date=datetime.now(), subscribe_begin=datetime.now(), subscribe_end=datetime.now(), category=category)
        
        return Topic.objects.create(name="Tópico Teste", subject=subject)

    def create_generic_resource(self):
        topic = self.create_topic()

        return Resource.objects.create(name="Recurso Teste", topic=topic)

    def test_str(self):
        topic = self.create_topic()

        self.assertEquals(str(topic), topic.name)

    def test_resource_str(self):
        resource = self.create_generic_resource()

        self.assertEquals(str(resource), resource.name)

    """
    We expect these to fail, since generic resource doesn't have a child
    """
    def test_resource_as_child(self):
        resource = self.create_generic_resource()

        self.assertRaises(AttributeError, lambda: resource.as_child())

    def test_resource_access_link(self):
        resource = self.create_generic_resource()

        self.assertRaises(AttributeError, lambda: resource.access_link())
    
    def test_resource_update_link(self):
        resource = self.create_generic_resource()

        self.assertRaises(AttributeError, lambda: resource.update_link())

    def test_resource_delete_message(self):
        resource = self.create_generic_resource()

        self.assertRaises(AttributeError, lambda: resource.delete_message())

    def test_resource_delete_link(self):
        resource = self.create_generic_resource()

        self.assertRaises(AttributeError, lambda: resource.delete_link())

    def test_resource_get_data_ini(self):
        resource = self.create_generic_resource()

        self.assertRaises(AttributeError, lambda: resource.get_data_ini())

    def test_resource_get_data_end(self):
        resource = self.create_generic_resource()

        self.assertRaises(AttributeError, lambda: resource.get_data_end())