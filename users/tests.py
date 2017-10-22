""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.test import TestCase, Client
from rolepermissions.shortcuts import assign_role
from django.core.urlresolvers import reverse
from .models import *
from .forms import *

#Create your tests here.
class TestUserCase(TestCase):

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

	# def test_edit_users(self):
	# 	self.client.login(username='test', password='testing')

	# 	url = reverse('users:edit_profile', kwargs={'username': self.user.username})        
	# 	data = EditUserForm().data
	# 	data['email'] = "testing2@amadeus.com"

	# 	response = self.client.put(url, data, format='json')       
	# 	self.assertEqual(response.status_code, 200)        
	# 	self.assertEqual(response.data['email'], data['email'])

	def test_delete_users(self):
		self.user1 = User.objects.create_user(
			username = "user1",
			email = 'user1@user1.com',
			password = 'user1test',
			cpf = '11111111111'
			)
		self.user2 = User.objects.create_user(
			username = "user2",
			email = 'user2@user2.com',
			password = 'user2test',
			cpf = '53574660332'
			)
		self.user3 = User.objects.create_user(
			username = "user3",
			email = 'user3@user3.com',
			password = 'user3test',
			cpf = '63638052281'
			)
		self.client.login(username='user', password = 'testing')
		users = User.objects.all().count()
		url = reverse('users:delete',kwargs={'username': self.user2.username})
		self.assertEqual(User.objects.all().count(),users) #Before deleting
		response = self.client.post(url)
		self.assertEqual(User.objects.all().count(),users - 1) #After deleting one user, if OK, the user was removed successfully.








