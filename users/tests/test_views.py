from django.test import TestCase, Client
from django.urls import reverse

from users.models import User


class TestViews(TestCase):

    def test_user_login_get(self):
        client = Client()

        response = client.get(reverse("users:login"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_user_list_GET(self):
        client = Client()

        response = client.get(reverse('users:manage'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "users/list.html")
