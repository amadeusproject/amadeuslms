from django.test import TestCase
from rolepermissions.shortcuts import assign_role

from users.models import User
from courses.models import CourseCategory, Course, Subject, Topic
from forum.models import Forum, Post, PostAnswer

class PostAnswerTestCase (TestCase):

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

        self.answerStudent = PostAnswer.objects.create(
            user = self.user_student,
            post = self.post_professor,
            message = 'testing a post answer',
            modification_date = '2016-10-05',
            answer_date = '2016-10-04',
        )
        self.answerStudent.save()

        self.answerProfessor = PostAnswer.objects.create(
            user = self.user_professor,
            post = self.post_student,
            message = 'testing a post answer',
            modification_date = '2016-10-05',
            answer_date = '2016-10-04',
        )
        self.answerProfessor.save()

    def test_create_answer_post (self):
        list_answers = PostAnswer.objects.filter(user=self.user_professor).count()
        answer = PostAnswer.objects.create(
            user = self.user_professor,
            post = self.post_student,
            message = 'testing a post answer2',
            modification_date = '2016-10-05',
            answer_date = '2016-10-04',
        )
        answer.save()

        self.assertEquals (list_answers+1, PostAnswer.objects.filter(user=self.user_professor, post=self.post_student).count())

        list_answers = PostAnswer.objects.filter(user=self.user_student).count()
        answer = PostAnswer.objects.create(
            user = self.user_student,
            post = self.post_professor,
            message = 'testing a post answer2',
            modification_date = '2016-10-05',
            answer_date = '2016-10-04',
        )
        answer.save()

        self.assertEquals (list_answers+1, PostAnswer.objects.filter(user=self.user_student, post=self.post_professor).count())       

    def test_update_answer_post (self):
        self.answerStudent.message = 'updating a student answer post'
        self.answerStudent.save()
        answer = PostAnswer.objects.get(message='updating a student answer post')

        self.assertEquals(self.answerStudent, answer) 


        self.answerProfessor.message = 'updating a professor answer post'
        self.answerProfessor.save()
        answer = PostAnswer.objects.get(message='updating a professor answer post')

        self.assertEquals(self.answerProfessor, answer)

    def test_delete_answer_post (self):
        list_studentAnswers = PostAnswer.objects.filter(user=self.user_student).count()
        self.assertEquals(list_studentAnswers, 1)

        self.answerStudent.delete()
        list_studentAnswers = PostAnswer.objects.filter(user=self.user_student).count()
        self.assertEquals(list_studentAnswers, 0)
        
        list_professorAnswers = PostAnswer.objects.filter(user=self.user_professor).count()
        self.assertEquals(list_professorAnswers, 1)

        self.answerProfessor.delete()
        list_professorAnswers = PostAnswer.objects.filter(user=self.user_professor).count()
        self.assertEquals(list_professorAnswers, 0)
         