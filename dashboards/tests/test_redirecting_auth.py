from django.test import TestCase, Client, override_settings
from django.core.urlresolvers import resolve
from reports.views import ReportView
from subjects.models import Subject, Tag
from users.models import User
from topics.models import Topic, Resource
from chat.models import Conversation, TalkMessages
from categories.models import Category
from datetime import datetime
from log.models import Log
from django.db.models import Q
from django.http import HttpResponse, JsonResponse


class RedirectingRulesTest(TestCase):

	def setUp(self):
		self.c = Client()
		self.student = User.objects.create(username = "student01", email= "student01@amadeus.br")
		self.student.set_password("amadeus") #because of the hash function used
		self.student.save()
		if self.c.login(email="student01@amadeus.br", password="amadeus"):
			print("student01 logged in")


		self.student02 = User.objects.create(username= "student02", email = "student02@amadeus.br")
		self.student02.set_password("amadeus")
		self.student02.save()
		c1 = Category.objects.create(name ="test category", visible = True)
		c1.coordinators.add(self.student02)
		c1.save()


	@override_settings(STATICFILES_STORAGE = None) # added decorator
	def test_admin_connection(self):
		admin = User.objects.create_superuser(username="admin" ,email="admin@amadeus.br", password="amadeus")
		admin.save()
		self.c.logout()
		if self.c.login(email="admin@amadeus.br", password="amadeus"):
			print("admin logged in")

		response = self.c.get('/dashboards/general/')
		self.assertEqual(response.status_code, 200)
	
	@override_settings(STATICFILES_STORAGE = None) # added decorator
	def test_admin_dashboard_redirect(self):
		#as student 01 is already logged in
		response = self.c.get('/dashboards/general/')
		self.assertEqual(response.status_code, 302)
	
	@override_settings(STATICFILES_STORAGE = None) # added decorator
	def test_category_redirect(self):
		response = self.c.get('/dashboards/categories/')
		self.assertEqual(response.status_code, 302)
		print("a user which is not a coordinator is any category was redirected")

	@override_settings(STATICFILES_STORAGE = None) # added decorator
	def test_category_connection(self):
		self.c.logout()
		if self.c.login(email="student02@amadeus.br", password="amadeus"):
			print("student 02 logged in")

		response = self.c.get('/dashboards/categories/')

		self.assertEqual(response.status_code, 200)
		print("coordinator is accessing category dashboard")