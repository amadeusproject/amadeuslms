# coding=utf-8

from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from rolepermissions.shortcuts import assign_role

from courses.models import Category, Course, Subject
from users.models import User

class SubjectTestCase(TestCase):

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

	def test_subject_view(self):
		self.client.login(username='professor', password='testing')
		url = reverse('course:view_subject', kwargs={'slug':self.subject.slug})
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'subject/index.html')

		self.client.login(username='student', password='testing')
		url = reverse('course:view_subject',kwargs={'slug':self.subject.slug})
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'subject/index.html')

	def test_subject_create(self):
		self.client.login(username='professor', password='testing')
		subjects = self.course.subjects.all().count()
		url = reverse('course:create_subject',kwargs={'slug':self.course.slug})
		data = {
            "name": 'create subject test',
            "description":'description of the subject test',
            'visible': True,
        }
		response = self.client.post(url, data)
		self.assertEqual(subjects + 1, self.course.subjects.all().count()) # create a new subject

		self.client.login(username='student', password='testing')
		subjects = self.course.subjects.all().count()
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 403) # access denied
		self.assertEqual(subjects, self.course.subjects.all().count()) # don't create a new subject

	def test_subject_update(self):
		self.client.login(username='professor', password='testing')
		url = reverse('course:update_subject',kwargs={'slug':self.course.subjects.all()[0].slug})
		data = {
            "name": 'new name',
            "description":'description of the subject test',
            'visible': True,
        }
		self.assertEqual(self.course.subjects.all()[0].name, "Subject Test") # old name
		response = self.client.post(url, data)
		self.assertEqual(self.course.subjects.all()[0].name, 'new name') # new name

		self.client.login(username='student', password='testing')
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 403) # access denied
		self.assertEqual(self.subject.name, "Subject Test") # name don't change

	def test_subject_delete(self):
		self.client.login(username='professor', password='testing')
		subjects = self.course.subjects.all().count()
		url = reverse('course:delete_subject',kwargs={'slug':self.course.subjects.all()[0].slug})
		self.assertEqual(self.course.subjects.all().count(), subjects) # all subjects
		response = self.client.post(url)
		self.assertEqual(self.course.subjects.all().count(), subjects - 1) # after delete one subject

		self.client.login(username='student', password='testing')
		response = self.client.post(url)
		self.assertEqual(response.status_code, 403) # access denied
		self.assertEqual(self.subject.name, "Subject Test") # name don't change
