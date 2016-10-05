from django.test import TestCase, Client

from django.core.urlresolvers import reverse
from rolepermissions.shortcuts import assign_role

from users.models import User
from courses.models import Category, Course, Subject, Topic
from forum.models import Forum

class ForumDetailViewTestCase (TestCase):

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

		self.category = Category.objects.create(
			name = 'Category test',
			slug = 'category_test'
		)
		self.category.save()

		self.course = Course.objects.create(
			name = 'Course Test',
			slug = 'course_test',
			max_students = 50,
			init_register_date = '2016-08-26',
			end_register_date = '2016-10-01',
			init_date = '2016-10-05',
			end_date = '2017-10-05',
			category = self.category
		)
		self.course.save()

		self.subject = Subject.objects.create(
            name = 'Subject Test',
            slug='subject-test',
            description = "description of the subject test",
            visible = True,
            course = self.course,
            init_date = '2016-10-05',
            end_date = '2017-10-05',
        )
		self.subject.save()

		self.topic = Topic.objects.create(
            name = 'Topic Test',
            description = "description of the topic test",
            subject = self.subject,
            owner = self.user,
        )
		self.topic.save()

		self.forum = Forum.objects.create(
        	topic=self.topic,
        	name = 'forum test',
        	slug='forum-test',
        	description = 'description of the forum test',
        	create_date = '2016-10-02',
        	modification_date = '2016-10-03',
        	limit_date = '2017-10-05',
        )
		self.forum.save()

		self.url = reverse('course:forum:view', kwargs={'slug':self.forum.slug})

	def test_view_ok (self):
		self.client.login(username='test', password='testing')

		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'forum/forum_view.html')

	def test_context(self):
		self.client.login(username='test', password='testing')

		response = self.client.get(self.url)
		
		self.assertTrue('form' in response.context)
		self.assertTrue('forum' in response.context)
		self.assertTrue('title' in response.context)


