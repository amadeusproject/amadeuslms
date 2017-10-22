""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.test import TestCase, RequestFactory
from users.models import User
from django.contrib.auth.models import AnonymousUser
from .. import views

from ..models import Category
from django.shortcuts import render

class Index_Test(TestCase):

	def setUp(self):

		"""Set up all the variables we need for these test"""
		self.factory = RequestFactory()
		self.user = User.objects.create(username="felipe", email="felipe.bormann@gmail.com", password="teste")
		self.admin  = User.objects.create_superuser('admin', email = 'admin@teste.com', password = 'teste')
		self.coordinator = User.objects.create(username="coordinator", email="felipe@gmail.com", password="teste")
		#self.category = Category.objects.create(name="test", coordinators=self.coordinator)

	def test_index_get_not_admin(self):

		"""Tests if an  user can get into 'manage categories' page and be redirected"""
		request = self.factory.get('categories/')

		request.user = self.user

		response = views.IndexView.as_view()(request)
		
		self.assertEqual(response.status_code, 302)

	def test_index_get_unauth(self):

		"""Tests if an unauthenticated user can get into 'manage categories' page and be redirected"""

		request = self.factory.get('categories/')

		request.user = AnonymousUser()

		response = views.IndexView.as_view()(request)
		
		self.assertEqual(response.status_code, 302) #Which means it is been redirected to login page

	def test_create_category(self):
		"""Tests if an admin can access and the create_category page is displayed and rendered without errors"""

		request = self.factory.get('categories/create')
		request.user = self.admin

		response = views.CreateCategory.as_view()(request)

		self.assertEqual(response.status_code, 200)

		
		rendered = render(response, template_name = 'categories/create.html') #try to render the page, this one gives us more errors
		
			
	def test_create_category_unauth(self):
		"""Tests if an unauthenticated user can get into 'create categories' page and be redirected"""
		request = self.factory.get('categories/create')

		request.user = AnonymousUser()

		response = views.IndexView.as_view()(request)
		
		self.assertEqual(response.status_code, 302) #Which means it is been redirected to login page

	def test_create_category_not_admin(self):
		"""Tests if a non-admin user can get into 'create categories' page and be redirected"""
		request = self.factory.get('categories/create')
		request.user = self.user
		response = views.IndexView.as_view()(request)
		
		self.assertEqual(response.status_code, 302) #Which means it is been redirected to main page or login page

	def test_update_category_not_coordinator(self):

		request = self.factory.get('categories/create')
		request.user = self.user
		response = views.UpdateCategory.as_view()(request, self.category.slug)
		
		self.assertEqual(response.status_code, 302) #Which means it is been redirected to main page or login page

		