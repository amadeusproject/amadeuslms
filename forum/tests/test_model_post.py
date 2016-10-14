from django.test import TestCase
from rolepermissions.shortcuts import assign_role

from users.models import User
from courses.models import CourseCategory, Course, Subject, Topic
from forum.models import Forum, Post

class PostTestCase (TestCase):

    def setUp (self):
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

        self.post_professor = Post.objects.create(
            user = self.user_professor,
            message = 'posting a test on forum as professor',
            modification_date = '2016-11-09',
            post_date = '2016-10-03',
            forum = self.forum,
        )
        self.post_professor.save()

        self.post_student = Post.objects.create(
            user = self.user_student,
            message = 'posting a test on forum as student',
            modification_date = '2016-11-09',
            post_date = '2016-10-03',
            forum = self.forum,
        )
        self.post_student.save()

    def test_create_post_professor (self):
        post_professor = Post.objects.create(
            user = self.user_professor,
            message = 'posting',
            modification_date = '2016-11-09',
            post_date = '2016-10-03',
            forum = self.forum,
        )
        post_professor.save()

        self.assertEquals (post_professor, Post.objects.get(user=self.user_professor, message='posting'))

    def test_create_post_student (self):
        post_student = Post.objects.create(
            user = self.user_student,
            message = 'posting',
            modification_date = '2016-11-09',
            post_date = '2016-10-03',
            forum = self.forum,
        )
        post_student.save()

        self.assertEquals (post_student, Post.objects.get(user=self.user_student, message='posting'))        

    def test_update_post_professor (self):
        self.post_professor.message = 'updating a post as professor'
        self.post_professor.save()

        self.assertEquals(self.post_professor, Post.objects.all()[1]) 

    def test_update_post_student (self):
        self.post_student.message = 'updating a post as student'
        self.post_student.save()

        self.assertEquals(self.post_student, Post.objects.all()[1])

    def test_delete_post_professor (self):
        post = Post.objects.get(user=self.user_professor, message='posting a test on forum as professor')
        self.post_professor.delete()

        try:
            post = Post.objects.get(user=self.user_professor, message='posting a test on forum as professor')
        except:
            pass

    def test_delete_post_student (self):
        post = Post.objects.get(user=self.user_student, message='posting a test on forum as student')
        self.post_student.delete()

        try:
            post = Post.objects.get(user=self.user_student, message='posting a test on forum as student')
        except:
            pass