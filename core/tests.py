from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from rolepermissions.shortcuts import assign_role
from users.models import User
# from django.core import mail

class LoginTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username = 'test', email = 'testing@amadeus.com', is_staff = True, is_active = True, password = 'testing')
        assign_role(self.user, 'system_admin')

        self.url = reverse('core:home')

    def test_ok(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        data = {'username': 'test', 'password': 'testing'}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse("app:index"))

    def test_not_ok(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        data = {'username': 'test', 'password': 'senhaerrada'}
        response = self.client.post(self.url, data)
        self.assertTrue('message' in response.context)
        self.assertEquals(response.context['message'], "Email ou senha incorretos!")
