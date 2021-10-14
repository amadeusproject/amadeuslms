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

from datetime import datetime

from categories.models import Category
from log.models import Log
from security.models import Security
from subjects.models import Subject
from topics.models import Topic
from users.models import User
from webpage.models import Webpage

class TestViews(TestCase):
    testCategory = None
    invisibleCategory = None

    subject = None
    topic = None
    resource = None

    staff = None
    professor = None
    coordinator = None

    def setUp(self):
        self.create_users()
        self.create_categories()
        self.create_subject()
        self.create_topics()
        self.create_resources()

    def create_users(self):
        self.staff = User.objects.create(username = 'Admin', email = 'administrador@amadeus.br', password = 'amadeus', is_staff=True)
        self.coordinator = User.objects.create(username = 'Coordenador', email = 'coordenador@amadeus.br', password = 'amadeus')
        self.professor = User.objects.create(username = 'professor', email = 'professor@amadeus.br', password = 'amadeus')

    def create_categories(self):
        self.testCategory = Category.objects.create(name="Categoria 1")
        self.testCategory.coordinators.add(self.coordinator)
        self.testCategory.save()

        self.invisibleCategory = Category.objects.create(name="Categoria 2")
        self.invisibleCategory.coordinators.add(self.coordinator)
        self.invisibleCategory.save()

    def change_security_status(self, status):
        security = Security.objects.get(id=1)
        security.deny_category_edition = status
        security.save()
    
    def create_subject(self):
        if self.subject is None:
            self.subject = Subject.objects.create(name="Subject", visible=True, init_date=datetime.now(), end_date=datetime.now(), subscribe_begin=datetime.now(), subscribe_end=datetime.now(), category=self.invisibleCategory)
            self.subject.professor.add(self.professor)

    def create_topics(self):
        self.topic = Topic.objects.create(name="Tópico Teste", repository=False, visible=True, subject=self.subject)

    def create_resources(self):
        self.resource = Webpage.objects.create(name="Recurso Teste", content="teste", topic=self.topic, visible=True)

    def test_category_index_302(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("categories:index"))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:index"))

    def test_category_index(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("categories:index"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/list.html")

    def test_category_create_get_302(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("categories:create"), HTTP_REFERER="")

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:index"))

    def test_category_create_get(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("categories:create"), HTTP_REFERER="")
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/create.html")

        context = response.context
        self.assertIn("subjects_menu_active", context)
        self.assertEquals(context.get("template_extends"), "subjects/list.html")

    def test_category_create_get_with_referer(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("categories:create"), HTTP_REFERER="categories")
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/create.html")

        context = response.context
        self.assertIn("settings_menu_active", context)
        self.assertEquals(context.get("template_extends"), "categories/list.html")

    def test_category_create_post(self):
        data = {
            "name": "Categoria teste"
        }

        numberCategories = Category.objects.all().count()
        numberLogs = Log.objects.all().count()

        self.client.force_login(self.staff)
        response = self.client.post(reverse("categories:create"), data, follow=True, HTTP_REFERER="")

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('categories:index'))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('Category "%s" register successfully!')%(data["name"]), message.message)

        #Test if database changed
        self.assertTrue(Category.objects.filter(name=data['name']).exists())
        self.assertEquals(Category.objects.all().count(), numberCategories + 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="category", action="create", resource="category", context__category_name=data["name"]).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_category_replicate_get_404(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("categories:replicate", kwargs={"slug": "teste"}), HTTP_REFERER="")

        self.assertEquals(response.status_code, 404)

    def test_category_replicate_get_302(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("categories:replicate", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER="")

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:index"))

    def test_category_replicate_security_block(self):
        self.client.force_login(self.coordinator)
        self.change_security_status(True)
        response = self.client.get(reverse("categories:replicate", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER="")

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:index"))

    def test_category_replicate_coordinator(self):
        self.client.force_login(self.coordinator)
        self.change_security_status(False)
        response = self.client.get(reverse("categories:replicate", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER="")

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/create.html")

        self.assertEquals(response.context["form"].initial["name"], self.testCategory.name)
        self.assertEquals(response.context["form"].initial["description"], self.testCategory.description)
        self.assertEquals(response.context["form"].initial["visible"], self.testCategory.visible)
        self.assertIn(self.coordinator, response.context["form"].initial["coordinators"])

    def test_category_replicate_staff(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("categories:replicate", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER="")

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/create.html")

        self.assertEquals(response.context["form"].initial["name"], self.testCategory.name)
        self.assertEquals(response.context["form"].initial["description"], self.testCategory.description)
        self.assertEquals(response.context["form"].initial["visible"], self.testCategory.visible)
        self.assertIn(self.coordinator, response.context["form"].initial["coordinators"])

    def test_category_replicate_post_coordinator(self):
        data = {
            "name": "Categoria Replicada",
            "description": self.testCategory.description,
            "visible": self.testCategory.visible,
            "coordinators": [self.coordinator.id],
        }

        numberCategories = Category.objects.all().count()
        numberLogs = Log.objects.all().count()

        self.client.force_login(self.coordinator)
        self.change_security_status(False)
        response = self.client.post(reverse("categories:replicate", kwargs={"slug": self.testCategory.slug}), data, follow=True, HTTP_REFERER="")

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:index'))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('Category "%s" register successfully!')%(data["name"]), message.message)

        #Test if database changed
        self.assertTrue(Category.objects.filter(name=data['name']).exists())
        self.assertEquals(Category.objects.all().count(), numberCategories + 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="category", action="replicate", resource="category", context__replicated_category_name=self.testCategory.name).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_category_replicate_post(self):
        data = {
            "name": "Categoria Staff",
            "description": self.testCategory.description,
            "visible": self.testCategory.visible,
            "coordinators": [self.coordinator.id],
        }

        numberCategories = Category.objects.all().count()
        numberLogs = Log.objects.all().count()

        self.client.force_login(self.staff)
        response = self.client.post(reverse("categories:replicate", kwargs={"slug": self.testCategory.slug}), data, HTTP_REFERER="", follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('categories:index'))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('Category "%s" register successfully!')%(data["name"]), message.message)

        #Test if database changed
        self.assertTrue(Category.objects.filter(name=data['name']).exists())
        self.assertEquals(Category.objects.all().count(), numberCategories + 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="category", action="replicate", resource="category", context__replicated_category_name=self.testCategory.name).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_category_update_get_404(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("categories:update", kwargs={"slug": "teste"}), HTTP_REFERER="")

        self.assertEquals(response.status_code, 404)

    def test_category_update_get_302(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("categories:update", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER="")

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:index"))

    def test_category_update_security_block(self):
        self.client.force_login(self.coordinator)
        self.change_security_status(True)
        response = self.client.get(reverse("categories:update", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER="")

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:index"))

    def test_category_update_coordinator_with_referer(self):
        self.client.force_login(self.coordinator)
        self.change_security_status(False)
        response = self.client.get(reverse("categories:update", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER=reverse("categories:index"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/update.html")

        context = response.context
        self.assertIn("settings_menu_active", context)
        self.assertEquals(context.get("template_extends"), "categories/list.html")

    def test_category_update_get(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("categories:update", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER="")

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/update.html")

        context = response.context
        self.assertIn("subjects_menu_active", context)
        self.assertEquals(context.get("template_extends"), "subjects/list.html")

    def test_category_update_coordinator(self):
        data = {
            "name": self.testCategory.name,
            "description": "Testando update de categoria",
            "visible": self.testCategory.visible,
            "coordinators": [self.coordinator.id]
        }

        numberLogs = Log.objects.all().count()

        self.client.force_login(self.coordinator)
        self.change_security_status(False)
        
        #Making sure that the return_url is set:
        self.client.get(reverse("categories:update", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER=reverse("subjects:home"))
        
        response = self.client.post(reverse("categories:update", kwargs={"slug": self.testCategory.slug}), data, follow=True, HTTP_REFERER=reverse("subjects:home"))
        
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("subjects:home"))

        category = Category.objects.get(id=self.testCategory.id)

        #Test if database changed
        self.assertEquals(category.description, data["description"])

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="category", action="update", resource="category", context__category_id=self.testCategory.id).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_category_update(self):
        data = {
            "name": self.testCategory.name,
            "description": "Testando update de categoria como staff",
            "visible": self.testCategory.visible,
            "coordinators": [self.coordinator.id]
        }

        numberLogs = Log.objects.all().count()

        self.client.force_login(self.staff)
        response = self.client.post(reverse("categories:update", kwargs={"slug": self.testCategory.slug}), data, follow=True, HTTP_REFERER="")
        
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("categories:index"))

        category = Category.objects.get(id=self.testCategory.id)

        #Test if database changed
        self.assertEquals(category.description, data["description"])

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="category", action="update", resource="category", context__category_id=self.testCategory.id).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_category_update_invisible_propagation(self):
        data = {
            "name": self.invisibleCategory.name,
            "description": "Testando update de categoria",
            "visible": False,
            "coordinators": [self.coordinator.id]
        }

        self.client.force_login(self.staff)
        response = self.client.post(reverse("categories:update", kwargs={"slug": self.invisibleCategory.slug}), data, follow=True, HTTP_REFERER="")

        self.assertFalse(Subject.objects.filter(category=self.invisibleCategory, visible=True).exists())
        self.assertFalse(Topic.objects.filter(subject__category=self.invisibleCategory, visible=True).exists())
        self.assertFalse(Webpage.objects.filter(topic__subject__category=self.invisibleCategory, visible=True).exists())

    def test_category_delete_get_302(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("categories:delete", kwargs={"slug": self.testCategory.slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:index"))

    def test_category_delete_get_302_with_referer(self):
        self.client.force_login(self.professor)
        self.change_security_status(False)
        response = self.client.get(reverse("categories:delete", kwargs={"slug": self.testCategory.slug}), HTTP_REFERER=reverse("subjects:home"))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_category_delete_get_302_without_referer(self):
        self.client.force_login(self.professor)
        self.change_security_status(False)
        response = self.client.get(reverse("categories:delete", kwargs={"slug": self.testCategory.slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:index"))

    def test_category_delete_method_not_allowed(self):
        self.client.force_login(self.staff)
        response = self.client.put(reverse("categories:delete", kwargs={"slug": self.testCategory.slug}))

        self.assertEquals(response.status_code, 405)

    def test_category_delete_coordinator_security_block(self):
        self.client.force_login(self.coordinator)
        self.change_security_status(True)
        response = self.client.get(reverse("categories:delete", kwargs={"slug": self.testCategory.slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:index"))

    def test_category_delete_coordinator(self):
        self.client.force_login(self.coordinator)
        self.change_security_status(False)
        response = self.client.get(reverse("categories:delete", kwargs={"slug": self.testCategory.slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/delete.html")

    def test_category_delete_staff(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("categories:delete", kwargs={"slug": self.testCategory.slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/delete.html")

    def test_category_delete(self):
        categoryName = self.testCategory.name

        numberCategories = Category.objects.all().count()
        numberLogs = Log.objects.all().count()

        self.client.force_login(self.coordinator)
        self.change_security_status(False)
        response = self.client.delete(reverse("categories:delete", kwargs={"slug": self.testCategory.slug}), follow=True, HTTP_REFERER=reverse("subjects:index"))

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:index'))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('Category "%s" removed successfully!')%(categoryName), message.message)

        #Test if database has changed
        self.assertEquals(Category.objects.all().count(), numberCategories - 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="category", action="delete", resource="category", context__category_name=categoryName).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_category_unable_delete(self):
        categoryName = self.invisibleCategory.name

        numberCategories = Category.objects.all().count()
        numberLogs = Log.objects.all().count()

        self.client.force_login(self.staff)
        response = self.client.delete(reverse("categories:delete", kwargs={"slug": self.invisibleCategory.slug}), follow=True, HTTP_REFERER=reverse("categories:index"))

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('categories:index'))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "danger")
        self.assertIn(ugettext("The category cannot be removed, it contains one or more virtual enviroments attach."), message.message)

        #Test if database has changed
        self.assertTrue(Category.objects.filter(name=categoryName).exists())
        self.assertEquals(Category.objects.all().count(), numberCategories)

        #Test if log was created
        self.assertFalse(Log.objects.filter(component="category", action="delete", resource="category", context__category_name=categoryName).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs)

    def test_category_view_open(self):
        logsCounter = Log.objects.all().count()

        self.client.force_login(self.professor)
        response = self.client.get(reverse("categories:view_log", kwargs={"category": self.invisibleCategory.id}), {"action": "open"}, follow=True)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="category", action="view", resource="category", context__category_id=self.invisibleCategory.id).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)
        
        log_id = Log.objects.latest("id").id
        
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok", 'log_id': log_id})

    def test_category_view_close(self):
        logsCounter = Log.objects.all().count()

        self.client.force_login(self.professor)
        response = self.client.get(reverse("categories:view_log", kwargs={"category": self.invisibleCategory.id}), {"action": "open"})

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="category", action="view", resource="category", context__category_id=self.invisibleCategory.id).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)

        log_id = Log.objects.latest("id").id

        response = self.client.get(reverse("categories:view_log", kwargs={"category": self.invisibleCategory.id}), {"action": "close", "log_id": log_id}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok"})

        #Test if log was updated
        log = Log.objects.get(id=log_id)
        self.assertNotEqual(log.context["timestamp_end"], "-1")