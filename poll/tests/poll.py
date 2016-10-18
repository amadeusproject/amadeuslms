# coding=utf-8

from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from rolepermissions.shortcuts import assign_role

from courses.models import CourseCategory, Course, Subject, Topic
from poll.models import Poll
from users.models import User

class PollTestCase(TestCase):
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

        self.category = CourseCategory(
            name = 'Categoria Teste',
        )
        self.category.save()

        self.course = Course(
            name = 'Curso Teste',
            max_students = 50,
            objectivies = "",
            content = "",
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
            init_date = '2016-10-05',
            end_date = '2017-10-05',
        )
        self.subject.save()

        self.subject.professors.add(self.user_professor)

        self.topic = Topic(
            name = 'Topic Test',
            description = "description of the topic test",
            subject = self.subject,
            owner = self.user_professor,
            visible = True,
        )
        self.topic.save()

        self.poll = Poll(
            name = 'Poll Test',
            limit_date = '2016-10-05',
            topic = self.topic,
        )
        self.poll.save()

    def test_poll_create(self):
        url = reverse('course:poll:create_poll',kwargs={'slug':self.topic.slug})
        data = {
            "name": 'create poll test',
            "limit_date":'2016-10-06',
            "all_students":True,
        }
        
        self.client.login(username='student', password='testing')
        poll = self.topic.activities.all().count()
        response = self.client.post(url, data)
        self.assertEqual(poll, self.topic.activities.all().count()) # don't create a new poll

        self.client.login(username='professor', password='testing')
        poll = self.topic.activities.all().count()
        response = self.client.post(url, data)
        self.assertEqual(poll + 1, self.topic.activities.all().count()) # create a new poll

    def test_poll_update(self):
        self.client.login(username='professor', password='testing')
        url = reverse('course:poll:update_poll',kwargs={'slug':self.poll.slug})
        title_poll = 'new poll name'
        data = {
            "name": title_poll,
            "limit_date":'2016-11-06',
            "all_students":True,
        }
        self.assertNotEqual(title_poll, self.topic.activities.all()[self.topic.activities.all().count() - 1].name) # old name
        response = self.client.post(url, data)
        self.assertEqual(title_poll,self.topic.activities.all()[self.topic.activities.all().count() - 1].name) # new name
        poll_student = 'new poll name student'
        data = {
            "name": poll_student,
            "limit_date":'2016-11-06',
            "all_students":True,
        }
        self.client.login(username='student', password='testing')
        self.assertNotEqual(poll_student, self.topic.activities.all()[self.topic.activities.all().count() - 1].name) # old name
        response = self.client.post(url, data)
        self.assertNotEqual(poll_student, self.topic.activities.all()[self.topic.activities.all().count() - 1].name) # new name

    def test_poll_delete(self):
        url = reverse('course:poll:delete_poll',kwargs={'slug':self.poll.slug})
        self.client.login(username='student', password='testing')
        poll = self.topic.activities.all().count()
        response = self.client.post(url)
        self.assertEqual(poll,self.topic.activities.all().count())

        self.client.login(username='professor', password='testing')
        poll = self.topic.activities.all().count()
        response = self.client.post(url)
        self.assertEqual(poll - 1,self.topic.activities.all().count())
