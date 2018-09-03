""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch, MagicMock
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

	def test_signup_get(self):
		request = self.factory.get(reverse_lazy('users:signup'))

		request.user = AnonymousUser()

		response = views.RegisterUser.as_view()(request)

		self.assertEquals(response.status_code, 200)

	@patch('users.models.User.save', MagicMock(name="save"))
	def test_signup_post(self):
		data = {
			'username': 'Teste',
			'last_name': 'Amadeus',
			'email': 'teste@amadeus.com.br',
			'new_password': 'teste',
			'password2': 'teste'
		}

		response = self.client.post(reverse_lazy('users:signup'), data)

		self.assertEquals(response.status_code, 302)
		self.assertTrue(User.save.called)
		self.assertEquals(User.save.call_count, 2) #call with commit=False first and then saving it

	def test_forgot_pass_get(self):
		request = self.factory.get(reverse_lazy('users:forgot_pass'))

		request.user = AnonymousUser()

		response = views.ForgotPassword.as_view()(request)

		self.assertEquals(response.status_code, 200)