# coding=utf-8

from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from rolepermissions.shortcuts import assign_role

from courses.models import Course, Category
from users.models import User

class CourseViewTestCase(TestCase):

	def setUp(self):
		self.client = Client()
    	
		self.user = User.objects.create_user(username = 'test', email = 'testing@amadeus.com', is_staff = True, is_active = True, password = 'testing')
		assign_role(self.user, 'system_admin')

		category = Category(name = 'Categoria Teste', slug = 'categoria_teste')
		category.save()

		course = Course(name = 'Curso Teste', slug = 'curso_teste', max_students = 50, init_register_date = '2016-08-26', end_register_date = '2016-10-01', init_date = '2016-10-05', end_date = '2017-10-05', category = category)
		course.save()

		self.category = category
		self.course = course

	def test_index(self):
		self.client.login(username='test', password='testing')
		
		url = reverse('app:course:manage')
		
		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'course/index.html')

	def test_index_not_logged(self):
		url = reverse('app:course:manage')
		
		response = self.client.get(url, follow = True)

		self.assertRedirects(response, '%s?next=%s' % (reverse('home'), url), 302, 200)

	def test_create(self):
		self.client.login(username='test', password='testing')

		url = reverse('app:course:create')

		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'course/create.html')

	def test_create_not_logged(self):
		url = reverse('app:course:create')
		
		response = self.client.get(url, follow = True)

		self.assertRedirects(response, '%s?next=%s' % (reverse('home'), url), 302, 200)

	def test_create_no_permission(self):
		self.user = User.objects.create_user(username = 'student', email = 'student@amadeus.com', type_profile = 2, is_staff = False, is_active = True, password = 'testing')

		assign_role(self.user, 'student')

		self.client.login(username='student', password='testing')

		url = reverse('app:course:create')
		
		response = self.client.get(url)

		self.assertEquals(response.status_code, 403)


	def test_update(self):
		self.client.login(username = 'test', password = 'testing')

		url = reverse('app:course:update', kwargs = {'slug': self.course.slug})

		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'course/update.html')

	def test_update_not_logged(self):
		url = reverse('app:course:update', kwargs = {'slug': self.course.slug})
		
		response = self.client.get(url, follow = True)

		self.assertRedirects(response, '%s?next=%s' % (reverse('home'), url), 302, 200)

	def test_update_no_permission(self):
		self.user = User.objects.create_user(username = 'student', email = 'student@amadeus.com', type_profile = 2, is_staff = False, is_active = True, password = 'testing')

		assign_role(self.user, 'student')

		self.client.login(username='student', password='testing')

		url = reverse('app:course:update', kwargs = {'slug': self.course.slug})
		
		response = self.client.get(url)

		self.assertEquals(response.status_code, 403)

	def test_view(self):
		self.client.login(username = 'test', password = 'testing')

		url = reverse('app:course:view', kwargs = {'slug': self.course.slug})

		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'course/view.html')

	def test_update_not_logged(self):
		url = reverse('app:course:view', kwargs = {'slug': self.course.slug})
		
		response = self.client.get(url, follow = True)

		self.assertRedirects(response, '%s?next=%s' % (reverse('home'), url), 302, 200)