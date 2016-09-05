from django.test import TestCase, Client
from rolepermissions.shortcuts import assign_role
from django.core.urlresolvers import reverse
from .models import *
from .forms import *

# Create your tests here.
class TestCreateUser(TestCase):

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

	def test_edit_users(self):
		self.client.login(username='test', password='testing')

		url = reverse('users:edit_profile', kwargs={'pk': self.user.id})        
		data = EditUserForm(self.data['email']).data
		data['email'] = "testing2@amadeus.com"

		response = self.client.put(url, data, format='json')        
		self.assertEqual(response.status_code, 200)        
		self.assertEqual(response.data['email'], data['email'])





