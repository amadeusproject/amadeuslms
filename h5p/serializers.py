""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import os
import zipfile
import time
from django.conf import settings
from django.core.files import File
from rest_framework import serializers
from django.shortcuts import get_object_or_404

import json
from .base_plugin.classes import H5PDjango
from .base_plugin.module import h5pInsert, h5pGetContent
from .base_plugin.editor.editormodule import createContent

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer
from pendencies.serializers import PendenciesSerializer
from students_group.serializers import StudentsGroupSerializer
from users.serializers import UserBackupSerializer

from subjects.models import Tag, Subject
from topics.models import Topic, Resource
from pendencies.models import Pendencies
from students_group.models import StudentsGroup
from log.models import Log
from users.models import User

from .models import H5P, h5p_contents
from .forms import handleUploadedFile

class SimpleH5PSerializer(serializers.ModelSerializer):
    topic = TopicSerializer('get_subject')
    tags = TagSerializer(many = True)
    pendencies_resource = PendenciesSerializer(many = True)
    file = serializers.CharField(required = False, allow_blank = True, max_length = 255)

    def get_subject(self, obj):
        subject = self.context.get("subject", None)

        return subject

    def validate(self, data):
        files = self.context.get('files', None)

        if files:
            if data["file"] in files.namelist():
                file_path = os.path.join(settings.MEDIA_ROOT, data["file"])

                if os.path.isfile(file_path):
                    dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")
                    h5p_helper_path = os.path.join(settings.MEDIA_ROOT, 'h5pp', 'tmp')

                    if not os.path.exists(h5p_helper_path):
                        os.makedirs(h5p_helper_path)

                    path = files.extract(data["file"], dst_path)
                    tmph5pfile = files.extract(data["file"], h5p_helper_path)

                    new_name = os.path.join("h5p_resource","file_" + str(time.time()) + os.path.splitext(data["file"])[1])

                    os.rename(os.path.join(dst_path, path), os.path.join(settings.MEDIA_ROOT, new_name))
                    os.rename(tmph5pfile, os.path.join(h5p_helper_path, os.path.split(data["file"])[1]))
                    
                    data["tmph5pfile"] = os.path.join(h5p_helper_path, os.path.split(data["file"])[1])
                    data["folderpath"] = h5p_helper_path
                    data["file"] = new_name

                    if os.path.exists(os.path.join(h5p_helper_path, "h5p_resource")):
                        os.rmdir(os.path.join(h5p_helper_path, "h5p_resource"))
                else:
                    path = files.extract(data["file"], settings.MEDIA_ROOT)
            else:
                data["file"] = None
        else:
            data["file"] = None

        return data

    class Meta:
        model = H5P
        exclude = ('students', 'groups',)

    def create(self, data):
        topic = data['topic']

        request = self.context.get('request', None)

        h5p = None

        if not topic["id"] is None:
            if "subject" in topic:
                r_exits = Resource.objects.filter(topic__subject = topic["subject"], name__unaccent__iexact = data["name"])
            else:
                r_exits = Resource.objects.filter(topic__subject__id = topic["subject_id"], name__unaccent__iexact = data["name"])

            if not r_exits.exists():
                if topic['id'] == "":
                    topic_exist = Topic.objects.filter(subject = topic['subject'], name__unaccent__iexact = topic["name"])

                    if topic_exist.exists():
                        topic = topic_exist[0]
                    else:
                        topic = Topic.objects.create(name = topic['name'], subject = topic['subject'], repository = topic['repository'], visible = topic['visible'], order = topic['order'], description = topic['description'])
                    
                    data["topic"] = topic
                else:
                    data["topic"] = get_object_or_404(Topic, id = topic["id"])

                h5p_data = data
                
                pendencies = h5p_data["pendencies_resource"]
                del h5p_data["pendencies_resource"]

                if h5p_data["tmph5pfile"]:
                    interface = H5PDjango(request.user)
                    validator = interface.h5pGetInstance(
                        'validator', h5p_data['folderpath'], h5p_data['tmph5pfile'])

                    if validator.isValidPackage(False, False):
                        _mutable = request.POST._mutable

                        request.POST._mutable = True

                        request.POST["name"] = h5p_data["name"]
                        request.POST['file_uploaded'] = True
                        request.POST['disable'] = 0
                        request.POST['author'] = request.user.username
                        request.POST['h5p_upload'] = h5p_data['tmph5pfile']
                        request.POST['h5p_upload_folder'] = h5p_data['folderpath']

                        request.POST._mutable = _mutable

                        if h5pInsert(request, interface):
                            contentResource = h5p_contents.objects.all().order_by('-content_id')[0]

                            h5p = H5P()
                            h5p.name = h5p_data["name"]
                            h5p.brief_description = h5p_data["brief_description"]
                            h5p.show_window = h5p_data["show_window"]
                            h5p.all_students = h5p_data["all_students"]
                            h5p.visible = h5p_data["visible"]
                            h5p.order = h5p_data["order"]
                            h5p.topic = h5p_data["topic"]
                            h5p.file = h5p_data["file"]
                            h5p.data_ini = h5p_data["data_ini"]
                            h5p.data_end = h5p_data["data_end"]
                            h5p.h5p_resource = contentResource

                            h5p.save()

                            tags = data["tags"]

                            for tag in tags:
                                if not tag["name"] == "":
                                    if tag["id"] == "":
                                        tag = Tag.objects.create(name = tag["name"])
                                    else:
                                        tag = get_object_or_404(Tag, id = tag["id"])

                                    h5p.tags.add(tag)
                            
                            resource = get_object_or_404(Resource, id = h5p.id)

                            for pend in pendencies:
                                Pendencies.objects.create(resource = resource, **pend)

        return h5p

    def update(self, instance, data):
        return instance

class CompleteH5PSerializer(serializers.ModelSerializer):
    file = serializers.CharField(required = False, allow_blank = True, max_length = 255)
    topic = TopicSerializer('get_subject')
    tags = TagSerializer(many = True)
    pendencies_resource = PendenciesSerializer(many = True)
    groups = StudentsGroupSerializer('get_files', many = True)
    students = UserBackupSerializer('get_files', many = True)

    def get_subject(self, obj):
        subject = self.context.get("subject", None)

        return subject

    def get_files(self, obj):
        files = self.context.get("files", None)

        return files

    def validate(self, data):
        files = self.context.get('files', None)

        if files:
            if data["file"] in files.namelist():
                file_path = os.path.join(settings.MEDIA_ROOT, data["file"])

                if os.path.isfile(file_path):
                    dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")
                    h5p_helper_path = os.path.join(settings.MEDIA_ROOT, 'h5pp', 'tmp')

                    if not os.path.exists(h5p_helper_path):
                        os.makedirs(h5p_helper_path)

                    path = files.extract(data["file"], dst_path)
                    tmph5pfile = files.extract(data["file"], h5p_helper_path)

                    new_name = os.path.join("h5p_resource","file_" + str(time.time()) + os.path.splitext(data["file"])[1])

                    os.rename(os.path.join(dst_path, path), os.path.join(settings.MEDIA_ROOT, new_name))
                    os.rename(tmph5pfile, os.path.join(h5p_helper_path, os.path.split(data["file"])[1]))
                    
                    data["tmph5pfile"] = os.path.join(h5p_helper_path, os.path.split(data["file"])[1])
                    data["folderpath"] = h5p_helper_path
                    data["file"] = new_name

                    if os.path.exists(os.path.join(h5p_helper_path, "h5p_resource")):
                        os.rmdir(os.path.join(h5p_helper_path, "h5p_resource"))
                else:
                    path = files.extract(data["file"], settings.MEDIA_ROOT)
            else:
                data["file"] = None
        else:
            data["file"] = None

        return data

    class Meta:
        model = H5P
        fields = '__all__'

    def create(self, data):
        topic = data['topic']

        request = self.context.get('request', None)

        h5p = None

        if not topic["id"] is None:

            if "subject" in topic:
                r_exits = Resource.objects.filter(topic__subject = topic["subject"], name__unaccent__iexact = data["name"])
            else:
                r_exits = Resource.objects.filter(topic__subject__id = topic["subject_id"], name__unaccent__iexact = data["name"])

            if not r_exits.exists():
                if topic['id'] == "":
                    topic_exist = Topic.objects.filter(subject = topic['subject'], name__unaccent__iexact = topic["name"])

                    if topic_exist.exists():
                        topic = topic_exist[0]
                    else:
                        topic = Topic.objects.create(name = topic['name'], subject = topic['subject'], repository = topic['repository'], visible = topic['visible'], order = topic['order'], description = topic['description'])
                    
                    data["topic"] = topic
                else:
                    data["topic"] = get_object_or_404(Topic, id = topic["id"])

                h5p_data = data
                
                pendencies = h5p_data["pendencies_resource"]
                del h5p_data["pendencies_resource"]

                if h5p_data["tmph5pfile"]:
                    interface = H5PDjango(request.user)
                    validator = interface.h5pGetInstance(
                        'validator', h5p_data['folderpath'], h5p_data['tmph5pfile'])

                    if validator.isValidPackage(False, False):
                        _mutable = request.POST._mutable

                        request.POST._mutable = True

                        request.POST["name"] = h5p_data["name"]
                        request.POST['file_uploaded'] = True
                        request.POST['disable'] = 0
                        request.POST['author'] = request.user.username
                        request.POST['h5p_upload'] = h5p_data['tmph5pfile']
                        request.POST['h5p_upload_folder'] = h5p_data['folderpath']

                        request.POST._mutable = _mutable

                        if h5pInsert(request, interface):
                            contentResource = h5p_contents.objects.all().order_by('-content_id')[0]

                            h5p = H5P()
                            h5p.name = h5p_data["name"]
                            h5p.brief_description = h5p_data["brief_description"]
                            h5p.show_window = h5p_data["show_window"]
                            h5p.all_students = h5p_data["all_students"]
                            h5p.visible = h5p_data["visible"]
                            h5p.order = h5p_data["order"]
                            h5p.topic = h5p_data["topic"]
                            h5p.file = h5p_data["file"]
                            h5p.data_ini = h5p_data["data_ini"]
                            h5p.data_end = h5p_data["data_end"]
                            h5p.h5p_resource = contentResource

                            h5p.save()

                            tags = data["tags"]

                            for tag in tags:
                                if not tag["name"] == "":
                                    if tag["id"] == "":
                                        tag = Tag.objects.create(name = tag["name"])
                                    else:
                                        tag = get_object_or_404(Tag, id = tag["id"])

                                    h5p.tags.add(tag)
                            
                            students = data["students"]
                            subject = get_object_or_404(Subject, slug = self.context.get("subject", None))

                            for student_data in students:
                                logs = student_data["get_items"]
                                
                                if student_data["id"] == "":
                                    u_exist = User.objects.filter(email = student_data["email"])

                                    if not u_exist.exists():
                                        student = u_exist[0]

                                        for log in logs:
                                            log["user_id"] = student.id

                                            l_exists = Log.objects.filter(user_id = log["user_id"], user = log["user"], user_email = log["user_email"], action = log["action"], resource = log["resource"], component = log["component"], context = log["context"])

                                            if not l_exists.exists():
                                                Log.objects.create(**log)
                                    else:
                                        student = User()
                                        student.email = student_data["email"]
                                        student.username = student_data["username"]
                                        student.last_name = student_data["last_name"] 
                                        student.social_name = student_data["social_name"] 
                                        student.show_email = student_data["show_email"] 
                                        student.is_staff = student_data["is_staff"] 
                                        student.is_active = student_data["is_active"]
                                        student.image = student_data["image"]

                                        student.save()

                                        for log in logs:
                                            log["user_id"] = student.id

                                            Log.objects.create(**log)
                                else:
                                    student = get_object_or_404(User, id = student_data["id"])

                                    for log in logs:
                                        l_exists = Log.objects.filter(user_id = log["user_id"], user = log["user"], user_email = log["user_email"], action = log["action"], resource = log["resource"], component = log["component"], context = log["context"])

                                        if not l_exists.exists():
                                            Log.objects.create(**log)

                                h5p.students.add(student)
                                subject.students.add(student)

                            groups = data["groups"]


                            for group_data in groups:
                                g_exists = StudentsGroup.objects.filter(subject = subject, slug = group_data["slug"])

                                if g_exists.exists():
                                    group = g_exists[0]
                                else:
                                    group = StudentsGroup()
                                    group.name = group_data["name"]
                                    group.description = group_data["description"]
                                    group.subject = subject

                                    group.save()

                                    for participant in group_data["participants"]:
                                        p_user = get_object_or_404(User, email = participant["email"])

                                        group.participants.add(p_user)

                                h5p.groups.add(group)

                            resource = get_object_or_404(Resource, id = h5p.id)

                            for pend in pendencies:
                                Pendencies.objects.create(resource = resource, **pend)

        return h5p