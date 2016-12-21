from django.test import TestCase, RequestFactory
from users.models import User

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
