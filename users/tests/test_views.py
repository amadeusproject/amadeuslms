from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import AnonymousUser
from ..models import User
from .. import views

class User_Test(TestCase):

	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.create(username = 'erik', email = 'egz@cin.ufpe.br', password = 'amadeus')
		self.admin = User.objects.create_superuser('admin', email = 'admin@amadeus.com', password = 'teste')

	def test_login_get_uauth(self):
		request = self.factory.get(reverse_lazy('users:login'))

		request.user = AnonymousUser()

		response = views.login(request)

		self.assertEquals(response.status_code, 200)

	def test_login_get_auth(self):
		request = self.factory.get(reverse_lazy('users:login'))

		request.user = self.user

		response = views.login(request)

		self.assertEquals(response.status_code, 302)

	def test_login_post_ok(self):
		data = {
			'email': 'admin@amadeus.com',
			'password': 'teste'
		}

		response = self.client.post(reverse_lazy('users:login'), data)
		
		self.assertEquals(response.status_code, 302)

	def test_login_post_invalid(self):
		data = {
			'email': 'test@amadeus.com.br',
			'password': 'anything'
		}

		response = self.client.post(reverse_lazy('users:login'), data)

		messages = response.context['messages']

		self.assertEquals(response.status_code, 200)
		self.assertIsNotNone(messages) #checking if message was sent