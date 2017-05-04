from django.test import TestCase, Client, override_settings
from django.core.urlresolvers import resolve
from reports.views import ReportView
from subjects.models import Subject, Tag
from users.models import User
from topics.models import Topic, Resource
from chat.models import Conversation, TalkMessages
from datetime import datetime
from log.models import Log
from django.db.models import Q
from ..views import most_used_tags
from django.http import HttpResponse, JsonResponse

class APIDashBoardTest(TestCase):

	def setUp(self):
		self.c = Client()
		self.student = User.objects.create(username = "student01", email= "student01@amadeus.br", password="amadeus")
		if self.c.login(email="student01@amadeus.br", password="amadeus"):
			print("student01 logged in")


	def test_most_used_tags(self):
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
 
		
		expected_data = {'felipe': 2, 'b2': 1}
		data = self.c.get('/analytics/most_used_tags/')
		print(data)
		self.assertEqual(data, expected_data)
