""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase, RequestFactory

import json

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

from categories.models import Category
from subjects.models import Subject
from topics.models import Topic
from users.models import User
from webpage.models import Webpage
from log.models import Log

class TestViews(TestCase):
    subject = None
    invisibleSubject = None

    topic = None
    invisibleTopic = None

    resource = None

    student = None
    professor = None

    def setUp(self):
        self.create_users()
        self.create_subject()
        self.create_topics()
        self.create_resources()

    def create_users(self):
        self.student = User.objects.create(username = 'erik', email = 'egz@cin.ufpe.br', password = 'amadeus')
        self.professor = User.objects.create(username = 'professor', email = 'rpao@cin.ufpe.br', password = 'amadeus')

    def create_subject(self):
        if self.subject is None:
            category = Category.objects.create(name="Categoria Teste")
            category.coordinators.add(self.professor)

            self.subject = Subject.objects.create(name="Subject", visible=True, init_date=datetime.now(), end_date=datetime.now(), subscribe_begin=datetime.now(), subscribe_end=datetime.now(), category=category)
            self.subject.professor.add(self.professor)

            self.invisibleSubject = Subject.objects.create(name="Invisible Subject", visible=False, init_date=datetime.now(), end_date=datetime.now(), subscribe_begin=datetime.now(), subscribe_end=datetime.now(), category=category)
            self.invisibleSubject.professor.add(self.professor)

    def create_topics(self):
        self.topic = Topic.objects.create(name="Tópico Teste", repository=True, subject=self.subject)
        self.invisibleTopic = Topic.objects.create(name="Tópico Teste", repository=False, subject=self.invisibleSubject)

    def create_resources(self):
        self.resource = Webpage.objects.create(name="Recurso Teste", content="teste", topic=self.invisibleTopic, visible=True)
    
    def test_topic_create_404(self):
        response = self.client.get(reverse("topics:create", kwargs={"slug": "subject_teste"}))

        self.assertEquals(response.status_code, 404)

    def test_topic_create_302(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("topics:create", kwargs={"slug": self.subject.slug}))
        
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('subjects:home'))

    def test_topic_create_get(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("topics:create", kwargs={"slug": self.subject.slug}))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "topics/create.html")

    def test_topic_create_post(self):
        data = {
            "name": "Topico test",
            "description": "Teste",
            "visible": True,
            "repository": False
        }

        self.client.force_login(self.professor)
        response = self.client.post(reverse("topics:create", kwargs={"slug": self.subject.slug}), data, follow=True)
        
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:view', kwargs = {'slug': self.subject.slug}))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('Topic "%s" was created on virtual enviroment "%s" successfully!')%(data["name"], self.subject.name), message.message)

    def test_topic_create_make_invisible(self):
        data = {
            "name": "Topico test",
            "description": "Teste",
            "visible": True,
            "repository": False
        }

        self.client.force_login(self.professor)
        response = self.client.post(reverse("topics:create", kwargs={"slug": self.invisibleSubject.slug}), data, follow=True)

        newtopic = Topic.objects.latest("id")

        self.assertEquals(newtopic.visible, False)

    def test_topic_update_404(self):
        response = self.client.get(reverse("topics:update", kwargs={"sub_slug": "subject_teste", "slug": "teste"}))

        self.assertEquals(response.status_code, 404)

    def test_topic_update_302(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("topics:update", kwargs={"sub_slug": self.subject.slug, "slug": self.topic.slug}))
        
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('subjects:home'))

    def test_topic_update_get(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("topics:update", kwargs={"sub_slug": self.subject.slug, "slug": self.topic.slug}))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "topics/update.html")

    def test_topic_update_post(self):
        data = {
            "name": self.topic.name,
            "description": "Teste",
            "visible": True,
            "repository": self.topic.repository
        }

        self.client.force_login(self.professor)
        response = self.client.post(reverse("topics:update", kwargs={"sub_slug": self.subject.slug, "slug": self.topic.slug}), data, follow=True)
        
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:view', kwargs = {'slug': self.subject.slug}))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('Topic "%s" was updated on virtual enviroment "%s" successfully!')%(self.topic.name, self.subject.name), message.message)

    def test_topic_update_make_invisible(self):
        data = {
            "name": self.invisibleTopic.name,
            "description": "Testando",
            "visible": True,
            "repository": self.invisibleTopic.repository
        }

        self.client.force_login(self.professor)
        response = self.client.post(reverse("topics:update", kwargs={"sub_slug": self.invisibleSubject.slug, "slug": self.invisibleTopic.slug}), data, follow=True)

        newtopic = Topic.objects.get(pk=self.invisibleTopic.id)

        self.assertEquals(newtopic.visible, False)

        resource = Webpage.objects.filter(topic=self.invisibleTopic).first()
        self.assertEquals(resource.visible, False)

    def test_topic_delete_404(self):
        response = self.client.get(reverse("topics:delete", kwargs={"slug": "teste"}))

        self.assertEquals(response.status_code, 404)

    def test_topic_delete_302(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("topics:delete", kwargs={"slug": self.topic.slug}))
        
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('subjects:home'))

    def test_topic_delete_get(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("topics:delete", kwargs={"slug": self.topic.slug}))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "topics/delete.html")

    def test_topic_delete(self):
        topicName = self.topic.name

        self.client.force_login(self.professor)
        response = self.client.delete(reverse("topics:delete", kwargs={"slug": self.topic.slug}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:view', kwargs = {'slug': self.subject.slug}))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('Topic "%s" was removed from virtual enviroment "%s" successfully!')%(topicName, self.subject.name), message.message)

    def test_topic_unable_delete(self):
        self.client.force_login(self.professor)
        response = self.client.delete(reverse("topics:delete", kwargs={"slug": self.invisibleTopic.slug}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:view', kwargs = {'slug': self.invisibleSubject.slug}))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "danger")
        self.assertEquals(message.message, _('Could not remove this topic. It has one or more resources attached.'))

    def test_topic_view_open_404(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("topics:view_log", kwargs={"topic": 10}), {"action": "open"})

        self.assertEquals(response.status_code, 404)

    def test_topic_view_open(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("topics:view_log", kwargs={"topic": self.invisibleTopic.id}), {"action": "open"}, follow=True)

        log_id = Log.objects.latest("id").id

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok", 'log_id': log_id})

    def test_topic_view_close(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("topics:view_log", kwargs={"topic": self.invisibleTopic.id}), {"action": "open"})

        log_id = Log.objects.latest("id").id

        response = self.client.get(reverse("topics:view_log", kwargs={"topic": self.invisibleTopic.id}), {"action": "close", "log_id": log_id}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok"})
    
    def test_topic_update_order_404(self):
        self.client.force_login(self.student)

        data = [{
            "topic_id": 10,
            "topic_order": 1
        }]

        response = self.client.get(reverse("topics:update_order"), {"data": json.dumps(data)}, content_type="application/json")

        self.assertEquals(response.status_code, 404)
    
    def test_topic_update_order_no_data(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("topics:update_order"), content_type="application/json")

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "No data received"})

    def test_topic_update_order(self):
        self.client.force_login(self.student)

        data = [{
            "topic_id": self.invisibleTopic.id,
            "topic_order": 1
        }]

        response = self.client.get(reverse("topics:update_order"), {"data": json.dumps(data)}, content_type="application/json")

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok"})

    def test_topic_update_resource_order_404(self):
        self.client.force_login(self.student)

        data = [{
            "resource_id": 10,
            "resource_order": 1
        }]

        response = self.client.post(reverse("topics:update_resource_order"), {"data": json.dumps(data)})

        self.assertEquals(response.status_code, 404)

    def test_topic_update_resource_order_no_data(self):
        self.client.force_login(self.student)

        response = self.client.post(reverse("topics:update_resource_order"))

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "No data received"})

    def test_topic_update_resource_order(self):
        self.client.force_login(self.student)

        data = [{
            "resource_id": self.resource.id,
            "resource_order": 1
        }]

        response = self.client.post(reverse("topics:update_resource_order"), {"data": json.dumps(data)})

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok"})
    