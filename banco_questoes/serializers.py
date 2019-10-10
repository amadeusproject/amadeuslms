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
from django.db.models import Q
from django.conf import settings
from django.core.files import File
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from subjects.serializers import TagSerializer

from subjects.models import Tag, Subject

from .models import Question, Alternative

class AlternativeSerializer(serializers.ModelSerializer):
    alt_img = serializers.CharField(required = False, allow_blank = True, max_length = 255)

    def validate(self, data):
        files = self.context.get('files', None)

        if files:
            if data["alt_img"] in files.namelist():
                file_path = os.path.join(settings.MEDIA_ROOT, data["alt_img"])

                if os.path.isfile(file_path):
                    dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")

                    path = files.extract(data["alt_img"], dst_path)

                    new_name = os.path.join("questions", os.path.join("alternatives", "alternative_" + str(time.time()) + os.path.splitext(data["question_img"])[1]))

                    os.rename(os.path.join(dst_path, path), os.path.join(settings.MEDIA_ROOT, new_name))
                    
                    data["alt_img"] = new_name
                else:
                    path = files.extract(data["alt_img"], settings.MEDIA_ROOT)
            else:
                data["alt_img"] = None
        else:
            data["alt_img"] = None

        return data

    class Meta:
        model = Alternative
        exclude = ('question',)

class QuestionDatabaseSerializer(serializers.ModelSerializer):
    categories = TagSerializer(many = True)
    alt_question = AlternativeSerializer('get_files', many = True)
    question_img = serializers.CharField(required = False, allow_blank = True, max_length = 255)

    def get_subject(self, obj):
        subject = self.context.get("subject", None)

        return subject

    def get_files(self, obj):
        files = self.context.get("files", None)

        return files

    def validate(self, data):
        files = self.context.get('files', None)

        if files:
            if data["question_img"] in files.namelist():
                file_path = os.path.join(settings.MEDIA_ROOT, data["question_img"])

                if os.path.isfile(file_path):
                    dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")

                    path = files.extract(data["question_img"], dst_path)

                    new_name = os.path.join("questions","question_" + str(time.time()) + os.path.splitext(data["question_img"])[1])

                    os.rename(os.path.join(dst_path, path), os.path.join(settings.MEDIA_ROOT, new_name))
                    
                    data["question_img"] = new_name
                else:
                    path = files.extract(data["question_img"], settings.MEDIA_ROOT)
            else:
                data["question_img"] = None
        else:
            data["question_img"] = None

        return data

    class Meta:
        model = Question
        exclude = ('subject', )

    def create(self, data):
        question_data = data

        alternatives = question_data["alt_question"]
        del question_data["alt_question"]

        question = Question()
        question.enunciado = question_data["enunciado"]
        question.question_img = question_data["question_img"]
        question.subject = self.context.get("subject", None)

        question.save()

        tags = data["categories"]

        for tag in tags:
            if not tag["name"] == "":
                if tag["id"] == "":
                    if Tag.objects.filter(name = tag["name"]).exists():
                        tag = get_object_or_404(Tag, name = tag["name"])
                    else:
                        tag = Tag.objects.create(name = tag["name"])
                else:
                    tag = get_object_or_404(Tag, id = tag["id"])

                question.categories.add(tag)

        for alt in alternatives:
            Alternative.objects.create(question = question, **alt)

        return question