from django.test import TestCase, RequestFactory
from users.models import User
from django.contrib.auth.models import AnonymousUser
from .. import views

class Index_Test(TestCase):

	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.create(username="felipe", email="felipe.bormann@gmail.com", password="teste")

	def test_index_get_auth(self):
		request = self.factory.get('courses/')

		request.user = self.user

		response = views.IndexView.as_view()(request)
		
		self.assertEqual(response.status_code, 200)

	def test_index_get_unauth(self):

		request = self.factory.get('courses/')

		request.user = AnonymousUser()

		response = views.IndexView.as_view()(request)
		
		self.assertEqual(response.status_code, 302) #Which means it is been redirected to login page