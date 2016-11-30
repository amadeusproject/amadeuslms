from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rolepermissions.shortcuts import assign_role
from django.utils.translation import ugettext_lazy as _
from core.models import MimeType
from users.models import User
from files.models import TopicFile
from files.forms import FileForm, UpdateFileForm
from rolepermissions.verifications import has_object_permission
from courses.models import CourseCategory, Course, Subject, Topic

import os
FILE_DIR = os.path.dirname(os.path.abspath(__file__))

class FileTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_user(
            username = 'admin',
            email = 'testing@amadeus.com',
            is_staff = True,
            is_active = True,
            password = 'testing123'
        )
        assign_role(self.admin, 'system_admin')
        
        self.teacher = User.objects.create_user(
            username = 'teacher',
            email = 'teacherg@school.com',
            is_staff = False,
            is_active = True,
            password = 'teaching123'
        )
        assign_role(self.teacher, 'professor')

        self.teacher2 = User.objects.create_user(
            username = 'teacher2',
            email = 'teacherg2@school.com',
            is_staff = False,
            is_active = True,
            password = 'teaching123'
        )
        assign_role(self.teacher2, 'professor')

        self.student = User.objects.create_user(
            username = 'student',
            email = 'student@amadeus.com',
            is_staff = False,
            is_active = True,
            password = 'testing123',
            type_profile = 2
        )
        assign_role(self.student, 'student')

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
            description = "description of the subject test file",
            visible = True,
            init_date = '2016-10-05',
            end_date = '2017-10-05',
            course = self.course,
        )
        self.subject.save()

        self.subject.professors.add(self.teacher)

        self.topic = Topic(
            name = 'Topic Test',
            description = "description of the topic test file",
            subject = self.subject,
        )
        self.topic.save()

        """
            Manual upload file
            Change directory for a file in your computer and be happy...
        """
        upload_file = open( '/'.join([FILE_DIR, 'files/teste.png']), 'rb')
        self.file = SimpleUploadedFile(upload_file.name, upload_file.read())

    def test_create_file_ok(self):
        self.client.login(username='admin', password = 'testing123')
        
        files = TopicFile.objects.all().count()
        self.assertEqual(TopicFile.objects.all().count(), files) #Macthing no file 
        
        topic = Topic.objects.get(name = 'Topic Test')

        url = reverse('course:file:create_file', kwargs={'slug': topic.slug})
        data = {
            'name' : 'testFile',
            "file_url" : self.file
        }
        data['topic'] = topic
        
        # Get modal 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Create file
        response = self.client.post(url, data)
        file_created = TopicFile.objects.get(name = data['name'])
        self.assertEqual(TopicFile.objects.filter(name= file_created.name).exists(),True)
        self.assertEqual(TopicFile.objects.all().count(), files + 1) 
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(template_name = 'files/create_file.html')

    def test_create_file_form_errors(self):
        self.client.login(username='admin', password = 'testing123')
        
        files = TopicFile.objects.all().count()
        self.assertEqual(TopicFile.objects.all().count(), files) #Macthing no file 
        
        topic = Topic.objects.get(name = 'Topic Test')

        url = reverse('course:file:create_file', kwargs={'slug': topic.slug})
        data = {
            "file_url" : self.file
        }
        data['topic'] = topic
        
        # Get modal 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Create file
        response = self.client.post(url, data)
        self.assertFormError(response, 'form', 'name', 'Este campo é obrigatório.')
        self.assertEqual(TopicFile.objects.all().count(), files) 
        self.assertEqual(response.status_code, 400)
        
        # Test file too large
        upload_file = open( '/'.join([FILE_DIR, 'files/large.pdf']), 'rb')
        file = SimpleUploadedFile(upload_file.name, upload_file.read())
        data = {
            "name": 'File too large',
            "file_url": file
        }
        data['topic'] = topic
        
        # Get modal 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        #Create file
        response = self.client.post(url, data)
        self.assertFormError(response, 'form', 'file_url', 'File too large (Max 10MB)')
        self.assertEqual(TopicFile.objects.all().count(), files)
        self.assertEqual(response.status_code, 400)

    def test_update_file_ok(self):
        self.client.login(username='admin', password = 'testing123')
        
        topic = Topic.objects.get(name = 'Topic Test')
        
        # File type
        mime_type = MimeType.objects.create(
            typ = 'image/png',
            icon = 'photo'
        )
        self.file_update = TopicFile.objects.create(
            name = 'testingFile',
            file_url = self.file,
            file_type = mime_type,
            topic = topic
        )

        url = reverse('course:file:update_file', kwargs={'slug': self.file_update.slug})
        
        upload_file_update = open( '/'.join([FILE_DIR, 'files/update.png']), 'rb')
        new_file = SimpleUploadedFile(upload_file_update.name, upload_file_update.read())
        data = {
            'name' : 'updated',
            'file_url': new_file
        }

        # Get modal
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, data)
        self.assertEqual(TopicFile.objects.all()[0].name, 'updated') # new file name
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(template_name = 'files/update_file.html')

    def test_update_file_student_errors(self):
        # Student
        self.client.login(username='student', password = 'testing123')
        
        topic = Topic.objects.get(name = 'Topic Test')
        
        # File type
        mime_type = MimeType.objects.create(
            typ = 'image/png',
            icon = 'photo'
        )
        self.file_update = TopicFile.objects.create(
            name = 'testingFile',
            file_url = self.file,
            file_type = mime_type,
            topic = topic
        )

        url = reverse('course:file:update_file', kwargs={'slug': self.file_update.slug})
        
        upload_file_update = open( '/'.join([FILE_DIR, 'files/update.png']), 'rb')
        new_file = SimpleUploadedFile(upload_file_update.name, upload_file_update.read())
        data = {
            'name' : 'updated',
            'file_url': new_file
        }

        # Get modal
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(url, data)
        self.assertEqual(TopicFile.objects.all()[0].name, 'testingFile') # new file name
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(template_name = 'files/update_file.html')

        # Teacher
        self.client.logout()
        self.client.login(username='teacher2', password = 'testing123')

        # Get modal
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(url, data)
        self.assertEqual(TopicFile.objects.all()[0].name, 'testingFile') # new file name
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(template_name = 'files/update_file.html')

    def test_delete_file(self):
        self.client.login(username='admin', password = 'testing123')
        
        topic = Topic.objects.get(name = 'Topic Test')
        
        # File type
        mime_type = MimeType.objects.create(
            typ = 'image/png',
            icon = 'photo'
        )
        self.file_delete = TopicFile.objects.create(
            name = 'testingFile',
            file_url = self.file,
            file_type = mime_type,
            topic = topic
        )

        url = reverse('course:file:delete_file', kwargs={'slug': self.file_delete.slug})

        # Get modal
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url)
        self.assertEqual(TopicFile.objects.all().count(), 0) # new file name
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(template_name = 'files/delete_file.html')

    def test_delete_file_error_permissions(self):
        # Teacher without permission
        self.client.login(username='teacher2', password = 'testing123')
        
        topic = Topic.objects.get(name = 'Topic Test')
        
        # File type
        mime_type = MimeType.objects.create(
            typ = 'image/png',
            icon = 'photo'
        )
        self.file_delete = TopicFile.objects.create(
            name = 'testingFile',
            file_url = self.file,
            file_type = mime_type,
            topic = topic
        )

        url = reverse('course:file:delete_file', kwargs={'slug': self.file_delete.slug})

        # Get modal
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(url)
        self.assertEqual(TopicFile.objects.all().count(), 1) # new file name
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(template_name = 'files/delete_file.html')

        # Student
        self.client.logout()
        self.client.login(username='student', password = 'testing123')
        
        # Get modal
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(url)
        self.assertEqual(TopicFile.objects.all().count(), 1) # new file name
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(template_name = 'files/delete_file.html')



        

