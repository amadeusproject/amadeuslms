# coding=utf-8

from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from rolepermissions.shortcuts import assign_role

from courses.models import Category, Course, Subject, Topic
from users.models import User

class TopicTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_professor = User.objects.create_user(
            username = 'professor',
        	email = 'professor@amadeus.com',
        	is_staff = False,
        	is_active = True,
        	password = 'testing',
            type_profile = 1
        )
        assign_role(self.user_professor, 'professor')

        self.user_student = User.objects.create_user(
            username = 'student',
            email = 'student@amadeus.com',
            is_staff = False,
            is_active = True,
            password = 'testing',
            type_profile = 2
        )
        assign_role(self.user_student, 'student')

        self.category = Category(
            name = 'Categoria Teste',
            slug = 'categoria_teste'
        )
        self.category.save()

        self.course = Course(
            name = 'Curso Teste',
            slug = 'curso_teste',
            max_students = 50,
            init_register_date = '2016-08-26',
            end_register_date = '2016-10-01',
            init_date = '2016-10-05',
            end_date = '2017-10-05',
            category = self.category
        )
        self.course.save()

        self.subject = Subject(
            name = 'Subject Test',
            description = "description of the subject test",
            visible = True,
            course = self.course,
        )
        self.subject.save()
        self.subject.professors.add(self.user_professor)

        self.topic = Topic(
            name = 'Topic Test',
            description = "description of the topic test",
            subject = self.subject,
            owner = self.user_professor,
        )
        self.topic.save()

    def test_topic_create(self):
        self.client.login(username='professor', password='testing')
        topic = self.subject.topics.all().count()
        url = reverse('course:create_topic',kwargs={'slug':self.subject.slug})
        data = {
            "name": 'create topic test',
            "description":'description of the topic test',
        }
        response = self.client.post(url, data)
        self.assertEqual(topic + 1, self.subject.topics.all().count()) # create a new subject

        self.client.login(username='student', password='testing')
        topic = self.subject.topics.all().count()
        response = self.client.post(url, data)
        self.assertEqual(topic + 1, self.subject.topics.all().count()) # create a new subject

    def test_topic_update(self):
        self.client.login(username='professor', password='testing')
        url = reverse('course:update_topic',kwargs={'slug':self.subject.topics.all()[0].slug})
        data = {
            "name": 'new name',
            "description":'description of the subject test',
            'visible': True,
        }
        self.assertEqual(self.subject.topics.all()[0].name, "Topic Test") # old name
        response = self.client.post(url, data)
        self.assertEqual(self.subject.topics.all()[0].name, 'new name') # new name

        data = {
            "name": 'new name 2',
            "description":'description of the subject test',
            'visible': True,
        }
        self.client.login(username='student', password='testing')
        response = self.client.post(url, data)
        self.assertEqual(self.subject.topics.all()[0].name, 'new name 2') # new name
