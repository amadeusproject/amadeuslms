from django.test import TestCase, Client, override_settings
from django.core.urlresolvers import resolve
from reports.views import ReportView
from subjects.models import Subject
from users.models import User

from datetime import datetime

class ReportTest(TestCase):

	def setUp(self):
		self.c = Client()
		self.student = User.objects.create(username = "student01", email= "student01@amadeus.br", password="amadeus")
		if self.c.login(email="student01@amadeus.br", password="amadeus"):
			print("student01 logged in")

		self.subject = Subject.objects.create(name="subject", visible= True, init_date= datetime.now(), end_date= datetime.now(),
		subscribe_begin = datetime.now(), subscribe_end= datetime.now() )

		self.invisible_subject = Subject.objects.create(name="subject invisible", visible= False, init_date= datetime.now(), end_date= datetime.now(),
		subscribe_begin = datetime.now(), subscribe_end= datetime.now() )
		self.subject.students.add(self.student)
		self.professor = User.objects.create(username= "professor01", email= "professor01@amadeus.br", password="amadeus")
		self.subject.professor.add(self.professor)
		

	"""
	check if it's still possible to create a report
	"""
	@override_settings(STATICFILES_STORAGE = None) # added decorator because of Whitenoise error
	def test_access_report_create_view(self):
		self.c.logout() #to logout student of setup
		self.c.login(email="professor01@amadeus.br", password="amadeus") #use professor of subject as logged in
		response = self.c.get('/subjects/report/create/interactions/?subject_id='+ str(self.subject.id), follow = True)
		self.assertEqual(response.status_code, 200)
	
	@override_settings(STATICFILES_STORAGE = None) # added decorator
	def test_restrict_acess_to_student_report_view(self):
		"""
		test when an student from the subject tries to access the subject analytics report builder, it will redirect
		"""
		report_view =  self.c.get('/subjects/report/create/interactions/?subject_id='+ str(self.subject.id))
		
		self.assertEqual(report_view.url, "/subjects/home")
	