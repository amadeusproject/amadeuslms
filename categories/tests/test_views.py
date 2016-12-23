from django.test import TestCase, RequestFactory
from users.models import User
from django.contrib.auth.models import AnonymousUser
from .. import views

from django.shortcuts import render

class Index_Test(TestCase):

	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.create(username="felipe", email="felipe.bormann@gmail.com", password="teste")
		self.admin  = User.objects.create_superuser('admin', email = 'admin@teste.com', password = 'teste')

	def test_index_get_auth(self):
		request = self.factory.get('categories/')

		request.user = self.user

		response = views.IndexView.as_view()(request)
		
		self.assertEqual(response.status_code, 200)

	def test_index_get_unauth(self):

		request = self.factory.get('categories/')

		request.user = AnonymousUser()

		response = views.IndexView.as_view()(request)
		
		self.assertEqual(response.status_code, 302) #Which means it is been redirected to login page

	def test_create_category(self):
		request = self.factory.get('categories/create')
		request.user = self.admin

		response = views.CreateCategory.as_view()(request)

		self.assertEqual(response.status_code, 200)

		
		rendered = render(response, template_name = 'categories/create.html') #try to render the page, this one gives us more errors
		
			
	def test_create_category_unauth(self):
		request = self.factory.get('categories/create')

		request.user = AnonymousUser()

		response = views.IndexView.as_view()(request)
		
		self.assertEqual(response.status_code, 302) #Which means it is been redirected to login page
		