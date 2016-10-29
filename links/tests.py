from django.test import TestCase,Client
from django.core.urlresolvers import reverse
from rolepermissions.shortcuts import assign_role
from django.utils.translation import ugettext_lazy as _

from users.models import User
from .models import *
from .forms import *
from courses.models import CourseCategory, Course, Subject, Topic

# Create your tests here.
class LinkTestCase(TestCase):
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
        self.teacher = User.objects.create_user(
        	username = 'teacher',
        	email = 'teacherg@school.com',
        	is_staff = True,
        	is_active = True,
        	password = 'teaching'
        )
        assign_role(self.teacher, 'professor')

        self.user_student = User.objects.create_user(
            username = 'student',
            email = 'student@amadeus.com',
            is_staff = False,
            is_active = True,
            password = 'testing',
            type_profile = 2
        )
        assign_role(self.user_student, 'student')

        self.category = CourseCategory(
            name = 'Categoria Teste',
            slug = 'categoria_teste'
        )
        self.category.save()

        self.course = Course(
            name = 'Curso Teste',
            slug = 'curso_teste',
            max_students = 50,
            init_register_date = '2016-08-26',
            end_register_date = '2016-10-01',
            init_date = '2016-10-05',
            end_date = '2017-10-05',
            category = self.category,
            public = True,
        )
        self.course.save()
        self.subject = Subject(
            name = 'Subject Test',
            description = "description of the subject test",
            visible = True,
            init_date = '2016-10-05',
            end_date = '2017-10-05',
            course = self.course,
        )
        self.subject.save()
        self.subject.professors.add(self.teacher)

        self.topic = Topic(
            name = 'Topic Test',
            description = "description of the topic test",
            subject = self.subject,
            owner = self.teacher,
        )
        self.topic.save()
    '''
    def test_create_link(self):
        self.client.login(username='user', password = 'testing')
        links = Link.objects.all().count()
        self.assertEqual(Link.objects.all().count(),links) #Before creating the link
        url = reverse('course:create_link')
        data = {
        'name' : 'testinglink',
        "description" : 'testdescription',
        "link" : 'teste.com'
        }
        response = self.client.post(url, data,format = 'json')
        link1 = Link.objects.get(name = data['name']) #Link criado com os dados inseridos corretamente
        self.assertEqual(Link.objects.filter(name= link1.name).exists(),True) #Verificada existência do link
        self.assertEqual(Link.objects.all().count(),links+1) #After creating link1, if OK, the link was created successfully.
        self.assertEqual(response.status_code, 302) #If OK, User is getting redirected correctly.
        self.assertTemplateUsed(template_name = 'links/create_link.html')
        data = {
        'name' : 'testlink2',
        "description" : 'testdescription2',
        "link" : 'teste'
        }
        response = self.client.post(url, data,format = 'json')
        self.assertEqual(Link.objects.filter(name= data['name']).exists(),False) #Verificada não existência do link com campo errado
    '''
    def test_create_link_teacher(self):
        self.client.login(username='teacher', password = 'teaching')
        links = Link.objects.all().count()
        self.assertEqual(Link.objects.all().count(),links) #Before creating the link
        topic = Topic.objects.get(name = 'Topic Test')
        url = reverse('course:links:create_link',kwargs={'slug': topic.slug})
        data = {
        'name' : 'testinglink',
        "link_description" : 'testdescription',
        "link_url" : 'teste.com'
        }
        data['topic'] = topic
        response = self.client.post(url, data,format = 'json')
        link1 = Link.objects.get(name = data['name']) #Link criado com os dados inseridos corretamente
        self.assertEqual(Link.objects.filter(name= link1.name).exists(),True) #Verificada existência do link
        self.assertEqual(Link.objects.all().count(),links+1) #After creating link1, if OK, the link was created successfully.
        self.assertEqual(response.status_code, 302) #If OK, User is getting redirected correctly.
        self.assertTemplateUsed(template_name = 'links/create_link.html')
        data = {
        'name' : 'testlink2',
        "link_description" : 'testdescription2',
        "link_url" : 'teste',
        }
        data['topic'] = topic
        response = self.client.post(url, data,format = 'json')
        self.assertEqual(Link.objects.filter(name= data['name']).exists(),False) #Verificada não existência do link com campo errado

    def test_create_link_student(self):
        self.client.login(username='student', password = 'testing')
        topic = Topic.objects.get(name = 'Topic Test')
        links = Link.objects.all().count()
        self.assertEqual(Link.objects.all().count(),links) #Before creating the link
        url = reverse('course:links:create_link',kwargs={'slug': topic.slug})
        data = {
        'name' : 'testinglink',
        "description" : 'testdescription',
        "link" : 'teste.com'
        }
        data['topic'] = topic
        response = self.client.post(url, data,format = 'json')
        self.assertEqual(response.status_code, 403) #Status code = 403, Permissão negada para usuário estudante.

    def test_update_link(self):
         self.client.login(username='teacher', password = 'teaching')
         topic = Topic.objects.get(name = 'Topic Test')
         self.link = Link.objects.create(
         name = 'testinglink',
         link_description = 'testdescription',
         link_url = 'teste.com',
         topic = topic
         )
         url = reverse('course:links:update_link',kwargs={'slug': self.link.slug})
         print("slug",self.link.slug)
         data = {
            "name" : 'testinglink',
            "link_description":'new description',
            "link_url" : 'teste.com',
         }
         self.assertEqual(Link.objects.all()[0].link_description, "testdescription") # old description
         response = self.client.post(url, data)
         self.assertEqual(Link.objects.all()[0].link_description, 'new description') # new description
    def test_delete_link(self):
         topic = Topic.objects.get(name = 'Topic Test')
         self.link = Link.objects.create(
         name = 'testinglink',
         link_description = 'testdescription',
         link_url = 'teste.com',
         topic = topic
         )
         self.client.login(username='user', password = 'testing')
         links = Link.objects.all().count()
         deletedlink = Link.objects.get(name = self.link.name)
         url = reverse('course:links:delete_link',kwargs={'linkname': self.link.name})
         self.assertEqual(Link.objects.all().count(),links)
         response = self.client.post(url)
         self.assertEqual(Link.objects.all().count(),links - 1) #Objeto removido
         self.assertEqual(Link.objects.filter(name= deletedlink.name).exists(),False) #Objeto removido e sua não-existência verificada
         #self.assertEqual(Link.objects.filter(name= deletedlink.name).exists(),True) #Objeto removido e sua existência verificada, se ERRO, objeto foi removido com sucesso!
         self.assertEqual(response.status_code, 302) #If OK, User is getting redirected correctly.
