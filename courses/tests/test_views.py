# coding=utf-8

from django.test import TestCase, Client
from django.core.urlresolvers import reverse

class CourseViewTestCase(TestCase):

	def setUp(self):
		self.client = Client()
		self.url = reverse('app:course:manage')

	#def tearDown(self):
	#	pass

	def test_course_ok(self):
		response = self.client.get(self.url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'course/index.html')

	def test_course_error(self):
		pass