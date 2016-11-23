from django.test import TestCase, Client

from django.core.urlresolvers import reverse
from rolepermissions.shortcuts import assign_role

from users.models import User
from courses.models import CourseCategory

class ForumViewTestCase (TestCase):

	def setUp(self):

		self.user = User.objects.create_user(
			username = 'test',
			email = 'testing@amadeus.com',
			is_staff = True,
			is_active = True,
			password = 'testing'
		)
		assign_role(self.user, 'system_admin')

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

		self.category = CourseCategory.objects.create(
			name = 'Category Test'
		)
		self.category.save()


		self.client = Client()
		self.client.login(username='test', password='testing')
		
		self.client_professor = Client()
		self.client_professor.login (username='professor', password='testing')

		self.client_student = Client()
		self.client_student.login (username='student', password='testing')
		

######################### CreateCatView #########################

	def test_CreateCatView_ok (self):
		url = reverse('course:create_cat')
        
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		
		response = self.client_professor.get(url)
		self.assertEquals(response.status_code, 200)

		response = self.client_student.get(url)
		self.assertEquals(response.status_code, 403)

	def test_CreateCatView_context (self):
		url = reverse('course:create_cat')

		response = self.client.get(url)
		self.assertTrue('form' in response.context)

		response = self.client_professor.get(url)
		self.assertTrue('form' in response.context)

	def test_CreateCatView_form_error (self):
		url = reverse('course:create_cat')
		data = {'name':''}
		list_categories = CourseCategory.objects.all().count()

		response = self.client.post(url, data)
		self.assertEquals(list_categories, CourseCategory.objects.all().count())

		response = self.client_professor.post(url, data)
		self.assertEquals(list_categories, CourseCategory.objects.all().count())

	def test_CreateCatView_form_ok (self):
		url = reverse('course:create_cat')
		data = {
		'name':'Second Category', 
		}
		list_categories = CourseCategory.objects.all().count()

		response = self.client.post(url, data)
		self.assertEquals (response.status_code, 302)
		self.assertEquals(list_categories+1, CourseCategory.objects.all().count())

		data = {
		'name' : 'Third Category',
		}
		response = self.client_professor.post(url, data)
		self.assertEquals (response.status_code, 302)
		self.assertEquals(list_categories+2, CourseCategory.objects.all().count())


######################### UpdateCatView #########################

	def test_UpdateCatView_ok (self):
		url = reverse ('course:update_cat', kwargs={'slug':self.category.slug})

		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)

		response = self.client_professor.get(url)
		self.assertEquals(response.status_code, 200)

		response = self.client_student.get(url)
		self.assertEquals(response.status_code, 403)

	def test_UpdateCatView_context (self):
		url = reverse ('course:update_cat', kwargs={'slug':self.category.slug})

		response = self.client.get(url)
		self.assertTrue('form' in response.context)

		response = self.client_professor.get(url)
		self.assertTrue('form' in response.context)

	def test_UpdateCatView_form_error (self):
		url = reverse ('course:update_cat', kwargs={'slug':self.category.slug})
		data = {'name':''}

		response = self.client.post(url, data)
		self.assertEquals(response.status_code, 200)

		response = self.client_professor.post(url, data)
		self.assertEquals(response.status_code, 200)

	def test_UpdateCatView_form_ok (self):
		url = reverse('course:update_cat', kwargs={'slug':self.category.slug})
		data = {
		'name':'Category Updated',
		}

		self.assertEquals(CourseCategory.objects.all()[0].name, 'Category Test')
		response = self.client.post(url, data)
		self.assertEquals (response.status_code, 302)
		self.assertEquals(CourseCategory.objects.all()[0].name, 'Category Updated')
		category = CourseCategory.objects.get(name='Category Updated')

		data={'name':'Category Updated As Professor'}
		self.assertEquals(CourseCategory.objects.all()[0].name, 'Category Updated')
		response = self.client_professor.post(url, data)
		self.assertEquals (response.status_code, 302)
		self.assertEquals(CourseCategory.objects.all()[0].name, 'Category Updated As Professor')
		category = CourseCategory.objects.get(name='Category Updated As Professor')

######################### DeleteCatView #########################


	def test_DeleteCatView_ok (self):
		url = reverse('course:delete_cat', kwargs={'slug':self.category.slug})

		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		
		response = self.client_professor.get(url)
		self.assertEquals(response.status_code, 200)

		response = self.client_student.get(url)
		self.assertEquals(response.status_code, 302)

	def test_DeleteCatView (self):
		url = reverse('course:delete_cat', kwargs={'slug':self.category.slug})

		category = CourseCategory.objects.get (name='Category Test')
		self.assertEquals(CourseCategory.objects.filter(name='Category Test').count(), 1)
		response = self.client.post(url)
		self.assertEquals(CourseCategory.objects.filter(name='Category Test').count(), 0)


		category_professor = CourseCategory.objects.create(
			name = 'Category Professor'
		)
		category_professor.save()
		url = reverse('course:delete_cat', kwargs={'slug':category_professor.slug})
		category = CourseCategory.objects.get (name='Category Professor')
		self.assertEquals(CourseCategory.objects.filter(name='Category Professor').count(), 1)
		response = self.client_professor.post(url)
		self.assertEquals(CourseCategory.objects.filter(name='Category Professor').count(), 0)