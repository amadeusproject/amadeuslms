from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from rolepermissions.shortcuts import assign_role

from users.models import User
from courses.models import CourseCategory, Course, Subject, Topic
from forum.models import Forum
			
class ForumTestCase (TestCase):
	
    def setUp(self):
        self.user_professor = User.objects.create_user(
            username = 'professor',
        	email = 'professor@amadeus.com',
        	is_staff = False,
        	is_active = True,
        	password = 'testing',
            type_profile = 1
        )
        assign_role(self.user_professor, 'professor')

        self.user_student = User.objects.create_user(
            username = 'student',
            email = 'student@amadeus.com',
            is_staff = False,
            is_active = True,
            password = 'testing',
            type_profile = 2
        )
        assign_role(self.user_student, 'student')

        self.category = CourseCategory.objects.create(
            name = 'Categoria Teste',
            create_date='2016-10-07',
        )
        self.category.save()

        self.course = Course.objects.create(
            name = 'Curso Teste',
            slug = 'curso_teste',
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
            description = "description of the subject test",
            visible = True,
            course = self.course,
            init_date = '2016-10-05',
            end_date = '2017-10-05',
        )
        self.subject.save()
        self.subject.professors.add(self.user_professor)

        self.topic = Topic.objects.create(
            name = 'Topic Test',
            description = "description of the topic test",
            subject = self.subject,
            owner = self.user_professor,
        )
        self.topic.save()

        self.forum = Forum.objects.create(
            topic=self.topic,
            name = 'forum test',
            description = 'description of the forum test',
            create_date = '2016-10-02',
            modification_date = '2016-10-03',
            limit_date = '2017-10-05',
        )
        self.forum.save()

    def test_create_forum (self):
        list_forum = Forum.objects.all().count()
        
        forum = Forum.objects.create(
    		topic=self.topic,
    		name = 'forum test2',
    		description = 'description of the forum test',
        	create_date = '2016-10-02',
        	modification_date = '2016-10-03',
            limit_date = '2017-10-05',
    	)
        forum.save()

        self.assertEquals(list_forum+1, Forum.objects.all().count())

    def test_update_forum(self):
        list_forum = Forum.objects.all().count()        
        self.forum.name = 'forum test updated'
        self.forum.save()

        self.assertEquals(self.forum, Forum.objects.get(name='forum test updated'))
        self.assertEquals(list_forum, Forum.objects.all().count())

    def test_delete_forum (self):
        list_forum = Forum.objects.all().count()
        self.forum.delete()
        
        self.assertEquals(list_forum-1, Forum.objects.all().count())            