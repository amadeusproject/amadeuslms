""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.test import TestCase, Client, override_settings
from django.core.urlresolvers import resolve
from reports.views import ReportView
from subjects.models import Subject
from users.models import User
from topics.models import Topic
from chat.models import Conversation, TalkMessages
from datetime import datetime
from log.models import Log
from django.db.models import Q


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
		
		self.assertEqual(report_view.url, "/subjects/home/")
	

	@override_settings(STATICFILES_STORAGE = None)
	def test_message_data_from_view(self):
		"""
		test if I'm capturing the message data correctly in all scenarios
		"""
		
		#scenario 01: the number of messages a student receives from other students
		topic = Topic.objects.create(name="novo topico", subject= self.subject, visible = True)
		topic.save()
		student02 = User.objects.create(username="student02", email= "student02@gmail.com", password="amadeus")
		student02.save()
		conversation_01 = Conversation.objects.create(user_one = self.student, user_two = student02)

		#building messages 
		message01 = TalkMessages(text="hi", talk = conversation_01, subject = self.subject, user = self.student)
		message01.save()
		message02 = TalkMessages(text="hello, how are you?", talk = conversation_01, subject = self.subject, user = student02)
		message02.save()
		#get all conversations where a student of the subject is in and the amount of messages the hey sent to other students
		conversations = Conversation.objects.filter(Q(user_one = self.student) | Q(user_two = self.student) )
		
		amount_of_messages = TalkMessages.objects.filter(talk__in= conversations).count()
		print(amount_of_messages)
		self.assertEqual(3,3)