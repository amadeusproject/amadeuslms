""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase

import json

from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from log.models import Log
from webpage.models import Webpage
from subjects.models import Subject
from mural.models import GeneralPost, CategoryPost, SubjectPost, Comment, MuralFavorites

#Import factories
from categories.factories import RandomCategoryFactory
from subjects.factories import RandomSubjectFactory
from mural.factories import RandomGeneralPostFactory, RandomCategoryPostFactory, RandomSubjectPostFactory
from topics.factories import RandomTopicFactory
from users.factories import RandomUserFactory

class TestViews(TestCase):
    staff = None

    professors = None
    students = None

    categories = None
    subjects = None
    topics = None
    resources = []    
    generalPosts = None
    categoryPosts = None
    subjectPosts = None
    comments = []

    def setUp(self):
        self.create_users()
        self.create_categories()
        self.create_subjects()
        self.create_topics()
        self.create_resources()
        self.create_posts()
        self.create_comments()

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

    def create_topics(self):
        self.topics = RandomTopicFactory.create_batch(2, subject=self.subjects[12])
        self.topics += RandomTopicFactory.create_batch(2, subject=self.subjects[6])

    def create_resources(self):
        self.resources = []
        self.resources.append(Webpage.objects.create(name="Recurso Teste", content="teste", topic=self.topics[0], visible=True))
        self.resources.append(Webpage.objects.create(name="Testing", content="teste", topic=self.topics[3], visible=True))

    def create_posts(self):
        self.generalPosts = RandomGeneralPostFactory.create_batch(5, user=self.professors[0])
        self.generalPosts += RandomGeneralPostFactory.create_batch(5, user=self.students[5])

        self.categoryPosts = RandomCategoryPostFactory.create_batch(5, space=self.categories[1], user=self.professors[1])
        self.categoryPosts += RandomCategoryPostFactory.create_batch(5, space=self.categories[0], user=self.students[0])
        
        self.subjectPosts = RandomSubjectPostFactory.create_batch(5, space=self.subjects[12], user=self.professors[2])
        self.subjectPosts += RandomSubjectPostFactory.create_batch(5, space=self.subjects[6], user=self.students[3])
        self.subjectPosts += RandomSubjectPostFactory.create_batch(2, space=self.subjects[12], user=self.professors[2], resource=self.resources[0])

    def create_comments(self):
        self.comments = []
        self.comments.append(Comment.objects.create(comment="Comment test", post=self.subjectPosts[0], user=self.professors[2]))
        self.comments.append(Comment.objects.create(comment="Comment test 2", post=self.subjectPosts[0], user=self.professors[2]))
        self.comments.append(Comment.objects.create(comment="Comment test 3", post=self.subjectPosts[0], user=self.professors[2]))
        self.comments.append(Comment.objects.create(comment="Comment test 4", post=self.subjectPosts[0], user=self.professors[2]))

    def isListEqual(self, a, b):
        intersec = list(set(a).intersection(b))

        return len(intersec) == 0

    def test_general_index(self):
        self.client.force_login(self.professors[1])

        response = self.client.get(reverse("mural:manage_general"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/list.html")

        self.assertEquals(response.context["posts"].count(), len(self.generalPosts))
        self.assertTrue(self.isListEqual(response.context["posts"].values_list("post"), [x.post for x in self.generalPosts]))
        self.assertEquals(response.context["favorites"], "")
        self.assertEquals(response.context["mines"], "")
        self.assertFalse("subject" in response.context["totals"])

    def test_general_index_admin(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("mural:manage_general"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/list.html")

        self.assertEquals(response.context["posts"].count(), len(self.generalPosts))
        self.assertTrue(self.isListEqual(response.context["posts"].values_list("post"), [x.post for x in self.generalPosts]))
        self.assertEquals(response.context["favorites"], "")
        self.assertEquals(response.context["mines"], "")
        self.assertTrue("subject" in response.context["totals"])

    def test_general_create_get(self):
        self.client.force_login(self.professors[1])

        response = self.client.get(reverse("mural:create_general"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/_form.html")

    def test_general_create_form_invalid(self):
        self.client.force_login(self.professors[1])

        data = {
            "post": "",
            "action": "comment"
        }

        response = self.client.post(reverse("mural:create_general"), data)

        self.assertEquals(response.status_code, 400)

    def test_general_create(self):
        self.client.force_login(self.professors[1])

        data = {
            "post": "Testing mural creation",
            "action": "comment"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("mural:create_general"), data, follow=True)

        newPost = GeneralPost.objects.latest("id")

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:render_post", args=(newPost.id, "create", "gen",)))

        #Test if database changed
        self.assertTrue(GeneralPost.objects.filter(post=data['post']).exists())
        self.assertEquals(GeneralPost.objects.all().count(), len(self.generalPosts) + 1)

        #Test if log was created
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_general_update_get(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("mural:update_general", kwargs={"pk": self.generalPosts[0].id}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/_form.html")

    def test_general_create_form_invalid(self):
        self.client.force_login(self.professors[0])

        data = {
            "id": self.generalPosts[0].id,
            "post": "",
            "action": "comment"
        }

        response = self.client.post(reverse("mural:update_general", kwargs={"pk": self.generalPosts[0].id}), data)

        self.assertEquals(response.status_code, 400)

    def test_general_update(self):
        self.client.force_login(self.professors[0])

        postId = self.generalPosts[0].id

        data = {
            "id": postId,
            "post": "Testing mural update",
            "action": "comment"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("mural:update_general", kwargs={"pk": postId}), data, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:render_post", args=(postId, "update", "gen",)))

        #Test if database changed
        post = GeneralPost.objects.get(id = postId)

        self.assertEquals(post.post, data["post"])

        #Test if log was created
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_general_delete_get(self):
        self.client.force_login(self.professors[0])

        response = self.client.get(reverse("mural:delete_general", kwargs={"pk": self.generalPosts[0].id}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/delete.html")

    def test_general_delete_post(self):
        self.client.force_login(self.professors[0])

        postId = self.generalPosts[0].id

        numberPosts = GeneralPost.objects.all().count()
        numberLogs = Log.objects.all().count()

        response = self.client.delete(reverse("mural:delete_general", kwargs={"pk": postId}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:deleted_post"))

        #Test if database changed
        self.assertEquals(GeneralPost.objects.all().count(), numberPosts - 1)
        self.assertFalse(GeneralPost.objects.filter(id=postId).exists())

        #Test if log was created
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_category_index(self):
        self.client.force_login(self.professors[1])

        response = self.client.get(reverse("mural:manage_category"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/list_category.html")

        self.assertEquals(response.context["categories"].count(), 1)
        self.assertTrue(self.isListEqual(response.context["categories"].values_list("id"), [self.categories[1].id]))
        self.assertFalse("subject" in response.context["totals"])

    def test_category_index_admin(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("mural:manage_category"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/list_category.html")

        self.assertEquals(response.context["categories"].count(), len(self.categories))
        self.assertTrue(self.isListEqual(response.context["categories"].values_list("id"), [x.id for x in self.categories]))
        self.assertTrue("subject" in response.context["totals"])

    def test_category_load_post(self):
        self.client.force_login(self.professors[1])

        response = self.client.get(reverse("mural:load_category", args={self.categories[1].id}))

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))

        self.assertEquals(content["count"], len([x for x in self.categoryPosts if x.space.id == self.categories[1].id]))


    def test_category_create_get(self):
        self.client.force_login(self.professors[1])

        response = self.client.get(reverse("mural:create_category", kwargs={"slug": self.categories[1].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/_form.html")

    def test_category_create_form_invalid(self):
        self.client.force_login(self.professors[1])

        data = {
            "post": "",
            "action": "comment"
        }

        response = self.client.post(reverse("mural:create_category", kwargs={"slug": self.categories[1].slug}), data)

        self.assertEquals(response.status_code, 400)

    def test_category_create(self):
        self.client.force_login(self.professors[1])

        data = {
            "post": "Testing category mural creation",
            "action": "comment"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("mural:create_category", kwargs={"slug": self.categories[1].slug}), data, follow=True)

        newPost = CategoryPost.objects.latest("id")

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:render_post", args=(newPost.id, "create", "cat",)))

        #Test if database changed
        self.assertTrue(CategoryPost.objects.filter(post=data['post']).exists())
        self.assertEquals(CategoryPost.objects.all().count(), len(self.categoryPosts) + 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="create_post", resource="category", context__category_id=self.categories[1].id).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    
    def test_category_update_get(self):
        self.client.force_login(self.professors[1])

        response = self.client.get(reverse("mural:update_category", kwargs={"pk": self.categoryPosts[0].id}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/_form.html")

    def test_category_update_form_invalid(self):
        self.client.force_login(self.professors[1])

        data = {
            "post": "",
            "action": "comment"
        }

        response = self.client.post(reverse("mural:update_category", kwargs={"pk": self.categoryPosts[0].id}), data)

        self.assertEquals(response.status_code, 400)

    def test_category_update(self):
        self.client.force_login(self.professors[1])

        postId = self.categoryPosts[0].id

        data = {
            "id": postId,
            "post": "Testing category mural update",
            "action": "comment"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("mural:update_category", kwargs={"pk": postId}), data, follow=True)

        newPost = CategoryPost.objects.latest("id")

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:render_post", args=(postId, "update", "cat",)))

        #Test if database changed
        post = CategoryPost.objects.get(id = postId)
        self.assertEquals(post.post, data["post"])

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="edit_post", resource="category", context__post_id=postId).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_category_delete_get(self):
        self.client.force_login(self.professors[1])

        response = self.client.get(reverse("mural:delete_category", kwargs={"pk": self.categoryPosts[0].id}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/delete.html")

    def test_category_delete_post(self):
        self.client.force_login(self.professors[1])

        postId = self.categoryPosts[0].id

        numberPosts = CategoryPost.objects.all().count()
        numberLogs = Log.objects.all().count()

        response = self.client.delete(reverse("mural:delete_category", kwargs={"pk": postId}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:deleted_post"))

        #Test if database changed
        self.assertEquals(CategoryPost.objects.all().count(), numberPosts - 1)
        self.assertFalse(CategoryPost.objects.filter(id=postId).exists())

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="delete_post", resource="category", context__post_id=postId).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)


    def test_subject_index(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:manage_subject"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/list_subject.html")

        subjectsList = [x.id for x in self.subjects if self.professors[2] in x.professor.all()]

        self.assertEquals(response.context["subjects"].count(), len(subjectsList))
        self.assertTrue(self.isListEqual(response.context["subjects"].values_list("id"), subjectsList))
        self.assertFalse("subject" in response.context["totals"])

    def test_subject_index_admin(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("mural:manage_subject"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/list_subject.html")

        self.assertEquals(response.context["subjects"].count(), 10)
        self.assertTrue(self.isListEqual(response.context["subjects"].values_list("id"), [x.id for x in self.subjects][:10]))
        self.assertTrue("subject" in response.context["totals"])

    def test_subject_load_post(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:load_subject", args={self.subjects[12].id}))

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))

        self.assertEquals(content["count"], len([x for x in self.subjectPosts if x.space.id == self.subjects[12].id]))


    def test_subject_create_get(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:create_subject", kwargs={"slug": self.subjects[12].slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/_form.html")

    def test_subject_create_form_invalid(self):
        self.client.force_login(self.professors[2])

        data = {
            "post": "",
            "action": "comment"
        }

        response = self.client.post(reverse("mural:create_subject", kwargs={"slug": self.subjects[12].slug}), data)

        self.assertEquals(response.status_code, 400)

    def test_subject_create(self):
        self.client.force_login(self.professors[2])

        data = {
            "post": "Testing subject mural creation",
            "action": "comment"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("mural:create_subject", kwargs={"slug": self.subjects[12].slug}), data, follow=True)

        newPost = SubjectPost.objects.latest("id")

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:render_post", args=(newPost.id, "create", "sub",)))

        #Test if database changed
        self.assertTrue(SubjectPost.objects.filter(post=data['post']).exists())
        self.assertEquals(SubjectPost.objects.all().count(), len(self.subjectPosts) + 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="create_post", resource="subject", context__subject_id=self.subjects[12].id).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_subject_update_get(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:update_subject", kwargs={"pk": self.subjectPosts[0].id}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/_form.html")

    def test_subject_update_form_invalid(self):
        self.client.force_login(self.professors[2])

        data = {
            "post": "",
            "action": "comment"
        }

        response = self.client.post(reverse("mural:update_subject", kwargs={"pk": self.subjectPosts[0].id}), data)

        self.assertEquals(response.status_code, 400)

    def test_subject_update(self):
        self.client.force_login(self.professors[2])

        postId = self.subjectPosts[0].id

        data = {
            "id": postId,
            "post": "Testing subject mural update",
            "action": "comment"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("mural:update_subject", kwargs={"pk": postId}), data, follow=True)

        newPost = SubjectPost.objects.latest("id")

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:render_post", args=(postId, "update", "sub",)))

        #Test if database changed
        post = SubjectPost.objects.get(id = postId)
        self.assertEquals(post.post, data["post"])

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="edit_post", resource="subject", context__post_id=postId).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_subject_delete_get(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:delete_subject", kwargs={"pk": self.subjectPosts[0].id}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/delete.html")

    def test_subject_delete_post(self):
        self.client.force_login(self.professors[2])

        postId = self.subjectPosts[0].id

        numberPosts = SubjectPost.objects.all().count()
        numberLogs = Log.objects.all().count()

        response = self.client.delete(reverse("mural:delete_subject", kwargs={"pk": postId}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:deleted_post"))

        #Test if database changed
        self.assertEquals(SubjectPost.objects.all().count(), numberPosts - 1)
        self.assertFalse(SubjectPost.objects.filter(id=postId).exists())

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="delete_post", resource="subject", context__post_id=postId).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_subject_view_302(self):
        self.client.force_login(self.students[4])

        response = self.client.get(reverse("mural:subject_view", kwargs={"slug": self.subjects[12].slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_subject_view_404(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:subject_view", kwargs={"slug": "test"}), follow=True)

        self.assertEquals(response.status_code, 404)

    def test_subject_view(self):
        self.client.force_login(self.professors[2])

        logsCounter = Log.objects.all().count()

        response = self.client.get(reverse("mural:subject_view", kwargs={"slug": self.subjects[12].slug}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/subject_view.html")
        self.assertEquals(response.context["favorites"], "")
        self.assertEquals(response.context["mines"], "")

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="view", resource="subject", context__subject_name=self.subjects[12].name).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)

    def test_resource_view_302(self):
        self.client.force_login(self.students[4])

        response = self.client.get(reverse("mural:resource_view", kwargs={"slug": self.resources[0].slug}))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("subjects:home"))

    def test_resource_view_404(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:resource_view", kwargs={"slug": "test"}))

        self.assertEquals(response.status_code, 404)

    def test_resource_view(self):
        self.client.force_login(self.professors[2])

        logsCounter = Log.objects.all().count()

        response = self.client.get(reverse("mural:resource_view", kwargs={"slug": self.resources[0].slug}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/resource_view.html")
        self.assertEquals(response.context["favorites"], "")
        self.assertEquals(response.context["mines"], "")

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="view", resource="subject", context__resource_name=self.resources[0].name).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)

    def test_resource_create_form_invalid(self):
        self.client.force_login(self.professors[2])

        data = {
            "post": "",
            "action": "comment"
        }

        response = self.client.post(reverse("mural:create_resource", kwargs={"slug": self.subjects[12].slug, "rslug": self.resources[0].slug}), data)

        self.assertEquals(response.status_code, 400)

    def test_resource_create(self):
        self.client.force_login(self.professors[2])

        data = {
            "post": "Testing resoruce mural creation",
            "action": "comment"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("mural:create_resource", kwargs={"slug": self.subjects[12].slug, "rslug": self.resources[0].slug}), data, follow=True)

        newPost = SubjectPost.objects.latest("id")

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:render_post", args=(newPost.id, "create", "sub",)))

        #Test if database changed
        self.assertTrue(SubjectPost.objects.filter(post=data['post']).exists())
        self.assertEquals(SubjectPost.objects.all().count(), len(self.subjectPosts) + 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="create_post", resource="subject", context__resource_id=self.resources[0].id).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)


    def test_comment_create_get(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:create_comment", kwargs={"post": self.subjectPosts[0].id}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/_form_comment.html")

    def test_comment_create_form_invalid(self):
        self.client.force_login(self.professors[2])

        data = {
            "comment": ""
        }

        response = self.client.post(reverse("mural:create_comment", kwargs={"post": self.subjectPosts[0].id}), data)

        self.assertEquals(response.status_code, 400)

    def test_comment_create(self):
        self.client.force_login(self.professors[2])

        data = {
            "comment": "Testing category mural creation"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("mural:create_comment", kwargs={"post": self.subjectPosts[0].id}), data, follow=True)

        newPost = Comment.objects.latest("id")

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:render_comment", args=(newPost.id, "create",)))

        #Test if database changed
        self.assertTrue(Comment.objects.filter(comment=data['comment']).exists())
        self.assertEquals(Comment.objects.all().count(), len(self.comments) + 1)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="create_comment", resource="subject", context__subject_id=self.subjects[12].id).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    
    def test_comment_update_get(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:update_comment", kwargs={"pk": self.comments[0].id}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/_form_comment.html")

    def test_comment_update_form_invalid(self):
        self.client.force_login(self.professors[2])

        data = {
            "comment": ""
        }

        response = self.client.post(reverse("mural:update_comment", kwargs={"pk": self.comments[0].id}), data)

        self.assertEquals(response.status_code, 400)

    def test_comment_update(self):
        self.client.force_login(self.professors[2])

        postId = self.comments[0].id

        data = {
            "id": postId,
            "comment": "Testing comment mural update"
        }

        numberLogs = Log.objects.all().count()

        response = self.client.post(reverse("mural:update_comment", kwargs={"pk": postId}), data, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:render_comment", args=(postId, "update",)))

        #Test if database changed
        post = Comment.objects.get(id = postId)
        self.assertEquals(post.comment, data["comment"])

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="edit_comment", resource="subject", context__comment_id=postId).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_comment_delete_get(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:delete_comment", kwargs={"pk": self.comments[0].id}))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "mural/delete.html")

    def test_comment_delete_post(self):
        self.client.force_login(self.professors[2])

        postId = self.comments[0].id

        numberPosts = Comment.objects.all().count()
        numberLogs = Log.objects.all().count()

        response = self.client.delete(reverse("mural:delete_comment", kwargs={"pk": postId}), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, reverse("mural:deleted_comment"))

        #Test if database changed
        self.assertEquals(Comment.objects.all().count(), numberPosts - 1)
        self.assertFalse(Comment.objects.filter(id=postId).exists())

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="delete_comment", resource="subject", context__comment_id=postId).exists())
        self.assertEquals(Log.objects.all().count(), numberLogs + 1)

    def test_comments_load(self):
        self.client.force_login(self.professors[2])

        response = self.client.get(reverse("mural:load_comments", args={self.subjectPosts[0].id, 0}))

        self.assertEquals(response.status_code, 200)


    def test_category_view_open(self):
        logsCounter = Log.objects.all().count()

        self.client.force_login(self.professors[1])
        response = self.client.get(reverse("mural:view_log_cat", kwargs={"category": self.categories[1].id}), {"action": "open"}, follow=True)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="view", resource="category", context__category_id=self.categories[1].id).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)
        
        log_id = Log.objects.latest("id").id
        
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok", 'log_id': log_id})

    def test_category_view_close(self):
        logsCounter = Log.objects.all().count()

        self.client.force_login(self.professors[1])
        response = self.client.get(reverse("mural:view_log_cat", kwargs={"category": self.categories[1].id}), {"action": "open"})

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="view", resource="category", context__category_id=self.categories[1].id).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)

        log_id = Log.objects.latest("id").id

        response = self.client.get(reverse("mural:view_log_cat", kwargs={"category": self.categories[1].id}), {"action": "close", "log_id": log_id}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok"})

        #Test if log was updated
        log = Log.objects.get(id=log_id)
        self.assertNotEqual(log.context["timestamp_end"], "-1")


    def test_subject_view_open(self):
        logsCounter = Log.objects.all().count()

        self.client.force_login(self.professors[2])
        response = self.client.get(reverse("mural:view_log_sub", kwargs={"subject": self.subjects[12].id}), {"action": "open"}, follow=True)

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="view", resource="subject", context__subject_id=self.subjects[12].id).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)
        
        log_id = Log.objects.latest("id").id
        
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok", 'log_id': log_id})

    def test_subject_view_close(self):
        logsCounter = Log.objects.all().count()

        self.client.force_login(self.professors[2])
        response = self.client.get(reverse("mural:view_log_sub", kwargs={"subject": self.subjects[12].id}), {"action": "open"})

        #Test if log was created
        self.assertTrue(Log.objects.filter(component="mural", action="view", resource="subject", context__subject_id=self.subjects[12].id).exists())
        self.assertEquals(Log.objects.all().count(), logsCounter + 1)

        log_id = Log.objects.latest("id").id

        response = self.client.get(reverse("mural:view_log_sub", kwargs={"subject": self.subjects[12].id}), {"action": "close", "log_id": log_id}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"message": "ok"})

        #Test if log was updated
        log = Log.objects.get(id=log_id)
        self.assertNotEqual(log.context["timestamp_end"], "-1")


    def test_favorite_post(self):
        self.client.force_login(self.professors[2])

        numberFavorites = MuralFavorites.objects.all().count()

        response = self.client.get(reverse("mural:favorite", args={self.subjectPosts[0].id}), {"action": "favorite"}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"label": _("Unfavorite")})

        #Test if database changed
        self.assertEquals(MuralFavorites.objects.all().count(), numberFavorites + 1)
        self.assertTrue(MuralFavorites.objects.filter(post=self.subjectPosts[0], user=self.professors[2]).exists())

    def test_favorite_post(self):
        self.client.force_login(self.professors[2])

        numberFavorites = MuralFavorites.objects.all().count()

        response = self.client.get(reverse("mural:favorite", args={self.subjectPosts[0].id}), {"action": "favorite"}, follow=True)

        response = self.client.get(reverse("mural:favorite", args={self.subjectPosts[0].id}), {"action": "unfavorite"}, follow=True)

        self.assertEquals(response.status_code, 200)

        #Test if database changed
        self.assertEquals(MuralFavorites.objects.all().count(), numberFavorites)
        self.assertFalse(MuralFavorites.objects.filter(post=self.subjectPosts[0], user=self.professors[2]).exists())