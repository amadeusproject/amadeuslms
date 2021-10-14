""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase

import os
import io
import zipfile

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile

from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from datetime import datetime, timedelta
from django.utils.formats import get_format

from django.contrib.messages import get_messages

from categories.models import Category
from subjects.models import Subject, Tag
from webpage.models import Webpage
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
    topics = None
    resource = None
    subjectEndSubscribe = None

    def setUp(self):
        self.create_users()
        self.create_categories()
        self.create_subjects()
        self.create_topics()
        self.create_resources()

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

        self.subjectEndSubscribe = RandomSubjectFactory.create(category=self.categories[0], subscribe_begin=datetime.now() - timedelta(days=2), subscribe_end=datetime.now() - timedelta(days=1))

    def create_topics(self):
        self.topics = RandomTopicFactory.create_batch(2, subject=self.subjects[1])

    def create_resources(self):
        self.resource = Webpage.objects.create(name="Recurso Teste", content="teste", topic=self.topics[0], visible=True)
        self.resource.tags.add(Tag.objects.create(name="test"))

    def isListEqual(self, a, b):
        intersec = list(set(a).intersection(b))

        return len(intersec) == 0 

    def parse_date(self, date_val):
        """Parse date from string by DATE_INPUT_FORMATS of current language"""
        for item in get_format("DATE_INPUT_FORMATS"):
            try:
                return date_val.strftime(item)
            except (ValueError, TypeError):
                continue

        return ""
    
    def test_subject_home_staff(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("subjects:home"))
        
        subList = self.subjects + [self.subjectEndSubscribe]

        self.assertEquals(response.context["total_subs"], len(subList))
        self.assertTrue(self.isListEqual(response.context["subjects"].values_list("name"), [x.name for x in subList]))

    def test_subject_home_not_staff(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:home"))

        teacherSubjects = [x.name for x in self.subjects if self.professors[0] in x.professor.all()]
        equalLists = self.isListEqual(response.context["subjects"].values_list("name"), teacherSubjects)

        self.assertEquals(response.context["total_subs"], len(teacherSubjects))
        self.assertTrue(equalLists)

    def test_subject_index_staff(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("subjects:index"))

        self.assertEquals(response.context["categories"].count(), len(self.categories))
        self.assertTrue(self.isListEqual(response.context["categories"].values_list("name"), [x.name for x in self.categories]))

    def test_subject_index_not_staff(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:index"))

        teacherCategories = Category.objects.filter(subject_category__professor = self.professors[0]).distinct()

        self.assertEquals(response.context["categories"].count(), teacherCategories.count())
        self.assertTrue(self.isListEqual(response.context["categories"].values_list("name"), [x.name for x in teacherCategories.all()]))

    def test_subject_index_not_staff_all_option(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:index", kwargs={"option": "all"}))

        self.assertEquals(response.context["categories"].count(), len(self.categories))
        self.assertTrue(self.isListEqual(response.context["categories"].values_list("name"), [x.name for x in self.categories]))

    def test_subject_index_pagination_number_error(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:index"), {"page": "a"})

        self.assertEquals(response.status_code, 404)

    def test_subject_index_pagination_page_inexisting(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:index"), {"page": 10})

        self.assertEquals(response.status_code, 404)

    def test_subject_index_category_view(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:cat_view", kwargs={"slug": self.categories[0].slug}), {"page": "last"})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["cat_slug"], self.categories[0].slug)
        self.assertTemplateUsed(response, "subjects/list.html")

    def test_subject_get_list(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:load_view", kwargs={"slug": self.categories[0].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/_list.html")

    def test_subject_create_get_404(self):
        response = self.client.get(reverse("subjects:create", kwargs={"slug": "subject_teste"}))

        self.assertEquals(response.status_code, 404)

    def test_subject_create_302(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:create", kwargs={"slug": self.categories[0].slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_subject_create_get(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("subjects:create", kwargs={"slug": self.categories[0].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/create.html")

        self.assertEquals(response.context["form"].initial["category"], self.categories[0])

    def test_subject_create_post(self):
        self.client.force_login(self.staff)

        data = {
            "name": "Testando assunto",
            "visible": True,
            "professor": [self.professors[0].id],
            "init_date": self.parse_date(datetime.now() + timedelta(days=2)), 
            "end_date": self.parse_date(datetime.now() + timedelta(days=3)), 
            "subscribe_begin": self.parse_date(datetime.now()), 
            "subscribe_end": self.parse_date(datetime.now() + timedelta(days=1)), 
        }

        numberSubjects = Subject.objects.all().count()
        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("subjects:create", kwargs={"slug": self.categories[0].slug}), data, follow=True)
        
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:index'))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('The Subject "%s" was registered on "%s" Category successfully!')%(data["name"], self.categories[0].name), message.message)

        #Test if database changed
        self.assertTrue(Subject.objects.filter(name=data['name']).exists())
        self.assertEquals(Subject.objects.all().count(), numberSubjects + 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="subject", action="create", resource="subject", context__subject_name=data["name"]).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_subject_replicate_get_404(self):
        response = self.client.get(reverse("subjects:replicate", kwargs={"subject_slug": "subject_teste"}))

        self.assertEquals(response.status_code, 404)

    def test_subject_replicate_302(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:replicate", kwargs={"subject_slug": self.subjects[-1].slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_subject_replicate_get(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("subjects:replicate", kwargs={"subject_slug": self.subjects[-1].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/create.html")

        self.assertEquals(response.context["form"].initial["category"], self.categories[-1])
        self.assertEquals(response.context["form"].initial["description"], self.subjects[-1].description)
        self.assertEquals(response.context["form"].initial["name"], self.subjects[-1].name)
        self.assertEquals(response.context["form"].initial["visible"], self.subjects[-1].visible)
        self.assertTrue(self.isListEqual(response.context["form"].initial["professor"].values_list("username"), [x.username for x in self.subjects[-1].professor.all()]))
        self.assertEquals(response.context["form"].initial["tags"], ", ".join(
                self.subjects[-1].tags.all().values_list("name", flat=True)
            ))
        self.assertEquals(response.context["form"].initial["init_date"], self.subjects[-1].init_date.date())
        self.assertEquals(response.context["form"].initial["end_date"], self.subjects[-1].end_date.date())
        self.assertTrue(self.isListEqual(response.context["form"].initial["students"].values_list("username"), [x.username for x in self.subjects[-1].students.all()]))
        self.assertEquals(response.context["form"].initial["description_brief"], self.subjects[-1].description_brief)

    def test_subject_replicate_post(self):
        self.client.force_login(self.staff)

        self.categories[-1].visible = False
        self.categories[-1].save()

        data = {
            "name": "Replica de assunto",
            "visible": True,
            "professor": [self.professors[0].id],
            "init_date": self.parse_date(datetime.now() + timedelta(days=2)), 
            "end_date": self.parse_date(datetime.now() + timedelta(days=3)), 
            "subscribe_begin": self.parse_date(datetime.now()), 
            "subscribe_end": self.parse_date(datetime.now() + timedelta(days=1)), 
        }

        numberSubjects = Subject.objects.all().count()
        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("subjects:replicate", kwargs={"subject_slug": self.subjects[-1].slug}), data, follow=True)
        
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:index'))

        newSubject = Subject.objects.latest("id")
        self.assertEquals(newSubject.visible, False)

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('The Subject "%s" was registered on "%s" Category successfully!')%(data["name"], self.categories[-1].name), message.message)

        #Test if database changed
        self.assertTrue(Subject.objects.filter(name=data['name']).exists())
        self.assertEquals(Subject.objects.all().count(), numberSubjects + 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="subject", action="replicate", resource="subject", context__replicated_subject_name=self.subjects[-1].name).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_subject_update_get_404(self):
        response = self.client.get(reverse("subjects:update", kwargs={"slug": "subject_teste"}))

        self.assertEquals(response.status_code, 404)

    def test_subject_update_302(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:update", kwargs={"slug": self.subjects[0].slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_subject_update_get(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("subjects:update", kwargs={"slug": self.subjects[0].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/update.html")

    def test_subject_update_post(self):
        self.client.force_login(self.staff)

        data = {
            "name": self.subjects[0].name,
            "visible": True,
            "professor": [self.professors[0].id],
            "init_date": self.parse_date(datetime.now() + timedelta(days=2)), 
            "end_date": self.parse_date(datetime.now() + timedelta(days=3)), 
            "subscribe_begin": self.parse_date(datetime.now()), 
            "subscribe_end": self.parse_date(datetime.now() + timedelta(days=1)),
            "description": "Descrição teste de update de assunto"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("subjects:update", kwargs={"slug": self.subjects[0].slug}), data, follow=True)
        
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:index'))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(_('The Subject "%s" was updated on "%s" Category successfully!')%(data["name"], self.categories[0].name), message.message)

        subject = Subject.objects.get(id=self.subjects[0].id)

        #Test if database changed
        self.assertEquals(subject.description, data["description"])

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="subject", action="update", resource="subject", context__subject_name=data["name"]).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_subject_update_make_invisible(self):
        self.client.force_login(self.staff)

        self.categories[0].visible = False
        self.categories[0].save()

        data = {
            "name": self.subjects[1].name,
            "visible": True,
            "professor": [self.professors[0].id],
            "init_date": self.parse_date(datetime.now() + timedelta(days=2)), 
            "end_date": self.parse_date(datetime.now() + timedelta(days=3)), 
            "subscribe_begin": self.parse_date(datetime.now()), 
            "subscribe_end": self.parse_date(datetime.now() + timedelta(days=1)),
            "description": "Descrição teste de update de assunto"
        }

        response = self.client.post(reverse("subjects:update", kwargs={"slug": self.subjects[1].slug}), data, follow=True)

        subject = Subject.objects.get(id=self.subjects[1].id)
        topic = Topic.objects.get(id=self.topics[0].id)

        self.assertFalse(subject.visible)
        self.assertFalse(topic.visible)

    def test_subject_delete_get_404(self):
        response = self.client.get(reverse("subjects:delete", kwargs={"slug": "subject_teste"}))

        self.assertEquals(response.status_code, 404)

    def test_subject_delete_302(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:delete", kwargs={"slug": self.subjects[-1].slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_subject_delete_students_block(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("subjects:delete", kwargs={"slug": self.subjects[0].slug}))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        
        self.assertEquals(response.status_code, 200)
        
        self.assertIn(_(
                    "Subject can't be removed. The subject still possess students and learning"
                    " objects associated"
                ), messages)

        self.assertJSONEqual(response.content.decode("utf-8"), {"error": True, "url": reverse("subjects:index")})

    def test_subject_delete_topics_block(self):
        self.client.force_login(self.staff)

        self.subjects[1].students.clear()

        response = self.client.get(reverse("subjects:delete", kwargs={"slug": self.subjects[1].slug}))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        
        self.assertEquals(response.status_code, 200)
        
        self.assertIn(_(
                    "Subject can't be removed. The subject still possess students and learning"
                    " objects associated"
                ), messages)

        self.assertJSONEqual(response.content.decode("utf-8"), {"error": True, "url": reverse("subjects:index")})

    def test_subject_delete_get(self):
        self.client.force_login(self.staff)

        self.subjects[5].students.clear()

        response = self.client.get(reverse("subjects:delete", kwargs={"slug": self.subjects[5].slug}))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        
        self.assertEquals(response.status_code, 200)

    def test_subject_delete(self):
        self.client.force_login(self.staff)

        subjectName = self.subjects[-1].name

        numberSubjects = Subject.objects.all().count()
        numberLogs = Log.objects.all().count()

        response = self.client.delete(reverse("subjects:delete", kwargs={"slug": self.subjects[-1].slug}), follow=True)

        self.assertEquals(response.status_code, 200)

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertIn(_('Subject "%s" removed successfully!')%(subjectName), messages)

        #Test if database has changed
        self.assertEquals(Subject.objects.all().count(), numberSubjects - 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="subject", action="delete", resource="subject", context__subject_name=subjectName).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_subject_view_404(self):
        response = self.client.get(reverse("subjects:view", kwargs={"slug": "subject_teste"}))

        self.assertEquals(response.status_code, 404)

    def test_subject_view_302(self):
        self.client.force_login(self.students[-1])

        response = self.client.get(reverse("subjects:view", kwargs={"slug": self.subjects[0].slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_subject_view(self):
        self.client.force_login(self.professors[0])

        logsCounter = Log.objects.all().count()

        response = self.client.get(reverse("subjects:view", kwargs={"slug": self.subjects[0].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/view.html")

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="subject", action="access", resource="subject", context__subject_name=self.subjects[0].name).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)

    def test_subject_view_with_topic(self):
        self.client.force_login(self.professors[0])

        logsCounter = Log.objects.all().count()

        response = self.client.get(reverse("subjects:topic_view", kwargs={"slug": self.subjects[1].slug, "topic_slug": self.topics[0].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/view.html")

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="subject", action="access", resource="subject", context__subject_name=self.subjects[1].name).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)

    def test_subject_subscribe_404(self):
        self.client.force_login(self.students[5])

        response = self.client.get(reverse("subjects:subscribe", kwargs={"slug": "subject_teste"}), follow=True)

        self.assertEquals(response.status_code, 404)

    def test_subject_subscribe_get(self):
        self.client.force_login(self.students[5])

        response = self.client.get(reverse("subjects:subscribe", kwargs={"slug": self.subjects[0].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/subscribe.html")

    def test_subject_subscribe_post_date(self):
        self.client.force_login(self.students[10])

        logsCounter = Log.objects.all().count()
        studentsNumber = self.subjectEndSubscribe.students.all().count()

        response = self.client.post(reverse("subjects:subscribe", kwargs={"slug": self.subjectEndSubscribe.slug}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:home'))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "danger")
        self.assertIn(ugettext("Subscription date is due!"), message.message)

        subject = Subject.objects.get(id=self.subjectEndSubscribe.id)

        self.assertEquals(studentsNumber, subject.students.all().count())
        self.assertNotIn(self.students[10], subject.students.all())

        self.assertFalse(Log.objects.filter(component="subject", action="subscribe", resource="subject", context__subject_name=self.subjectEndSubscribe.name).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter)

    def test_subject_subscribe_post(self):
        self.client.force_login(self.students[10])

        logsCounter = Log.objects.all().count()
        studentsNumber = self.subjects[0].students.all().count()

        response = self.client.post(reverse("subjects:subscribe", kwargs={"slug": self.subjects[0].slug}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse('subjects:view', kwargs={"slug": self.subjects[0].slug}))

        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "success")
        self.assertIn(ugettext("Subscription was successfull!"), message.message)

        subject = Subject.objects.get(id=self.subjects[0].id)

        self.assertEquals(studentsNumber + 1, subject.students.all().count())
        self.assertIn(self.students[10], subject.students.all())

        self.assertTrue(Log.objects.filter(component="subject", action="subscribe", resource="subject", context__subject_name=self.subjects[0].name).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 2)

    def test_subject_search_blank(self):
        self.client.force_login(self.students[5])

        response = self.client.get(reverse("subjects:search"), {"search": ""}, HTTP_REFERER=reverse("subjects:home"))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_subject_search(self):
        self.client.force_login(self.students[0])

        logsCounter = Log.objects.all().count()

        response = self.client.get(reverse("subjects:search", kwargs={"option": "resources"}), {"search": "test"}, follow=True, HTTP_REFERER=reverse("subjects:home"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/list_search.html")

        self.assertEquals(response.context["totals"]["resources_count"], 1)
        self.assertEquals(response.context["totals"]["subjects_count"], 0)

        self.assertTrue(Log.objects.filter(component="subject", action="search", resource="subject/resources", context__search_for="test").exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)

    def test_subject_view_open(self):
        logsCounter = Log.objects.all().count()

        self.client.force_login(self.professors[0])
        response = self.client.get(reverse("subjects:view_log", kwargs={"subject": self.subjects[0].id}), {"action": "open"}, follow=True)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="subject", action="view", resource="subject", context__subject_id=self.subjects[0].id).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)
        
        log_id = Log.objects.latest("id").id
        
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok", 'log_id': log_id})

    def test_subject_view_close(self):
        logsCounter = Log.objects.all().count()

        self.client.force_login(self.professors[0])
        response = self.client.get(reverse("subjects:view_log", kwargs={"subject": self.subjects[0].id}), {"action": "open"})

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="subject", action="view", resource="subject", context__subject_id=self.subjects[0].id).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)

        log_id = Log.objects.latest("id").id

        response = self.client.get(reverse("subjects:view_log", kwargs={"subject": self.subjects[0].id}), {"action": "close", "log_id": log_id}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok"})

        #Test if log was updated
        log = Log.objects.get(id=log_id)
        self.assertNotEqual(log.context["timestamp_end"], "-1")

    def test_subject_get_participants(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:get_participants", kwargs={"subject": self.subjects[0].slug}))

        profs = self.subjects[0].professor.all().exclude(email=self.professors[0].email)
        studs = self.subjects[0].students.all()

        self.assertEquals(len(response.context["participants"]), profs.count() + studs.count())
        self.assertTrue(self.isListEqual([u.username for u in response.context["participants"]], [x for x in profs.union(studs).values_list("username")]))

    def test_subject_toggle_view(self):
        self.client.force_login(self.professors[0])
        
        response = self.client.get(reverse("subjects:toggle_student_visualization", kwargs={"subject": self.subjects[0].slug}))

        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok"})

    def test_subject_backup_404(self):
        response = self.client.get(reverse("subjects:backup", kwargs={"slug": "subject_teste"}))

        self.assertEquals(response.status_code, 404)

    def test_subject_backup_302(self):
        self.client.force_login(self.students[0])

        response = self.client.get(reverse("subjects:backup", kwargs={"slug": self.subjects[1].slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_subject_backup_get(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:backup", kwargs={"slug": self.subjects[1].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/backup.html")

        self.assertEquals(response.context["topics"].count(), len(self.topics))
        self.assertTrue(self.isListEqual(response.context["topics"].values_list("name"), [x.name for x in self.topics]))

    def test_subject_backup_post(self):
        self.client.force_login(self.professors[0])

        data = {
            "resource[]": [self.resource.id]
        }

        response = self.client.post(reverse("subjects:do_backup", kwargs={"subject": self.subjects[1].slug}), data)

        self.assertEquals(response.get('Content-Disposition'), "attachment; filename=backup.zip")

        try:
            f = io.BytesIO(response.content)
            zipped_file = zipfile.ZipFile(f, 'r')

            self.assertIsNone(zipped_file.testzip())        
            self.assertIn('backup.json', zipped_file.namelist())
        finally:
            zipped_file.close()
            f.close()

    def test_subject_backup_post_with_participants(self):
        self.client.force_login(self.professors[0])

        data = {
            "resource[]": [self.resource.id],
            "participants": True
        }

        response = self.client.post(reverse("subjects:do_backup", kwargs={"subject": self.subjects[1].slug}), data)

        self.assertEquals(response.get('Content-Disposition'), "attachment; filename=backup.zip")

        try:
            f = io.BytesIO(response.content)
            zipped_file = zipfile.ZipFile(f, 'r')

            self.assertIsNone(zipped_file.testzip())        
            self.assertIn('backup.json', zipped_file.namelist())
        finally:
            zipped_file.close()
            f.close()

    def test_subject_restore_404(self):
        response = self.client.get(reverse("subjects:restore", kwargs={"slug": "subject_teste"}))

        self.assertEquals(response.status_code, 404)

    def test_subject_restore_302(self):
        self.client.force_login(self.students[0])

        response = self.client.get(reverse("subjects:restore", kwargs={"slug": self.subjects[0].slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_subject_restore_get(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("subjects:restore", kwargs={"slug": self.subjects[0].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "subjects/restore.html")
    
    def test_subject_restore_post(self):
        self.client.force_login(self.professors[0])

        data = {
            "resource[]": [self.resource.id]
        }

        response = self.client.post(reverse("subjects:do_backup", kwargs={"subject": self.subjects[1].slug}), data)

        numberTopics = self.subjects[0].topic_subject.all().count()

        try:
            f = io.BytesIO(response.content)
            fi = File(f)
            filepath = "backup.zip"
            
            with default_storage.open(filepath, 'wb+') as dest:
                for chunk in fi.chunks():
                    dest.write(chunk)
            
            with default_storage.open(filepath, "rb") as attach:
                response = self.client.post(reverse("subjects:do_restore", kwargs={"subject": self.subjects[0].slug}), {"zip_file": attach}, follow=True)
            
            self.assertEquals(response.status_code, 200)
            self.assertRedirects(response, reverse("subjects:restore", kwargs={"slug": self.subjects[0].slug}))

            message = list(response.context.get("messages"))[0]

            self.assertEquals(message.tags, "success")
            self.assertIn(ugettext("Backup restored successfully!"), message.message)

            subject = Subject.objects.get(id=self.subjects[0].id)

            self.assertEquals(subject.topic_subject.all().count(), numberTopics + 1)
            self.assertTrue(Webpage.objects.filter(topic__subject__id=self.subjects[0].id).exists())
        finally:
            default_storage.delete(filepath)
            f.close()

        