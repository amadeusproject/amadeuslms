from django.test import TestCase,Client
from django.core.urlresolvers import reverse
from rolepermissions.shortcuts import assign_role

from users.models import User
from .models import *

# Create your tests here.
class LinkTestCase(TestCase):
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
    def test_create_link(self):
        self.client.login(username='user', password = 'testing')
        links = Link.objects.all().count()
        self.assertEqual(Link.objects.all().count(),links) #Before creating the link
        url = reverse('course:create_link')
        data = {
        'name' : 'testinglink',
        "description" : 'testdescription',
        "link" : 'teste.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(Link.objects.all().count(),links+1) #After creating one link, if OK, the link was created successfully.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name = 'links/link_modal.html')
    # def test_update_link():
    #     pass
    def test_delete_link(self):
         self.link = Link.objects.create(
         name = 'testinglink',
         description = 'testdescription',
         link = 'teste.com'
         )
         self.client.login(username='user', password = 'testing')
         links = Link.objects.all().count()
         url = reverse('course:delete_link',kwargs={'linkname': self.link.name})
         self.assertEqual(Link.objects.all().count(),links)
         response = self.client.get(url)
         self.assertEqual(Link.objects.all().count(),links - 1)
         self.assertEqual(response.status_code, 200)
