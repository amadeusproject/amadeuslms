from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from rolepermissions.shortcuts import assign_role
from users.models import User
from django.core import mail

class LoginTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username = 'test',
            email = 'testing@amadeus.com',
            is_staff = True,
            is_active = True,
            password = 'testing'
        )
        assign_role(self.user, 'system_admin')

        self.url = reverse('core:home')

    def test_ok(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        data = {'username': 'test', 'password': 'testing'}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse("app:index"))

    # def test_not_ok(self):
    #     response = self.client.get(self.url)
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'index.html')
    #     data = {'username': 'test', 'password': 'senhaerrada'}
    #     response = self.client.post(self.url, data)
    #     self.assertTrue('message' in response.context)
    #     self.assertEquals(response.context['message'], "Email ou senha incorretos!")

class RegisterUserTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('core:register')
        self.data = {
                'username': 'testeamadeus',
                'email': 'teste@amadeus.com',
                'password': 'aminhasenha1',
                'password2': 'aminhasenha1',
                'name': 'Teste Amadeus',
                'city': 'Praia',
                'state': 'PE',
                'gender': 'F',
            }

    def test_register_ok(self):

        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, 'http://localhost%s' % reverse('core:home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)

class RememberPasswordTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('core:remember_password')

    def test_remember_password_ok(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'remember_password.html')
        data = {'email': 'fulano@fulano.com', 'registration': '0124578964226'}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 1)
        self.assertTrue('success' in response.context)
        self.assertTrue('danger' not in response.context)

    def test_remember_password_error(self):
        data = {'email': 'fulano@fulano.com','registration':''}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 0)
        self.assertTrue('success' not in response.context)
        self.assertTrue('danger' in response.context)

        data = {'email': '', 'registration': '0124578964226'}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 0)
        self.assertTrue('success' not in response.context)
        self.assertTrue('danger' in response.context)


class UpdateUserTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.url = reverse('users:update_user')

    def test_get_post(self):
        data={
                'username': 'testeamadeus',
                'email': 'teste@amadeus.com',
                'name': 'Teste Amadeus',
                'city': 'Praia',
                'state': 'PE',
                'gender': 'F',
            }
        # self.assertRedirects(response1, reverse('app:index'))
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
