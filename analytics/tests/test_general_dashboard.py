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
from ..views import most_used_tags, most_accessed_subjects
from django.http import HttpResponse, JsonResponse

class APIDashBoardTest(TestCase):

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
		self.category = Category(name= "category 01")
		self.category.save()

	def test_most_used_tags(self):

		"""
		testing if the catches all tags used in a resource and in a subject
		"""
		t = Tag(name="felipe")
		t.save()
		t1 = Tag(name="b2")
		t1.save()

		s1 = Subject.objects.create(name="subject", visible= True, init_date= datetime.now(), end_date= datetime.now(),
		subscribe_begin = datetime.now(), subscribe_end= datetime.now() )
		s1.tags.add(t)
		s1.save()
		s2 = Subject.objects.create(name="subject dois", visible= True, init_date= datetime.now(), end_date= datetime.now(),
		subscribe_begin = datetime.now(), subscribe_end= datetime.now() )
		s2.tags.add(t)
		s2.save()
		r1 = Resource.objects.create(name="resource um")
		r1.tags.add(t1)
		r1.save()
 
		
		expected_data = [{'name': 'felipe', 'count': 2}, {'name':'b2', 'count': 1}]
		data = self.c.get('/analytics/most_used_tags/')
		self.assertEqual(data.status_code, 200 )
		self.assertJSONEqual(str(data.content, encoding='UTF-8'), expected_data)

	@override_settings(STATICFILES_STORAGE = None) # added decorator
	def test_most_accessed_subjects(self):
		"""
		test if we collect the correct amount of access to a subject
		"""
		s1 = Subject.objects.create(name="subject", visible= True, init_date= datetime.now(), end_date= datetime.now(),
		subscribe_begin = datetime.now(), subscribe_end= datetime.now() )
		s1.students.add(self.student)
		s1.students.add(self.student02)
		s1.category = self.category
		s1.save()

		response = self.c.get('/subjects/view/'+str(s1.slug)+'/')
		print(response)
		self.assertEqual(response.status_code, 200)

		self.c.logout() #logout student one
		if self.c.login(email="student02@amadeus.br", password="amadeus"):
			print("student02 logged in")

		response = self.c.get('/subjects/view/'+str(s1.slug)+'/')
		self.assertEqual(response.status_code, 200)
		
		response = self.c.get('/analytics/most_accessed_subjects/')
		self.assertEqual(response.status_code, 200)	
		expected_data = [{'name': s1.name, 'count': 2}]
		self.assertJSONEqual(str(response.content, encoding = 'UTF-8'), expected_data)




	def test_most_accessed_categories(self):
		self.fail("finish the test")

	def test_most_active_users(self):
		self.fail("finish the test")
