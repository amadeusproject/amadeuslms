import os
import zipfile
import time
from django.conf import settings
from django.core.files import File
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer
from pendencies.serializers import PendenciesSerializer
from students_group.serializers import StudentsGroupSerializer
from users.serializers import UserBackupSerializer

from subjects.models import Tag
from topics.models import Topic, Resource
from pendencies.models import Pendencies

from .models import PDFFile

class SimplePDFFileSerializer(serializers.ModelSerializer):
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
			file_path = os.path.join(settings.MEDIA_ROOT, data["file"])

			if os.path.isfile(file_path):
				dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")

				path = files.extract(data["file"], dst_path)

				new_name = "files/file_" + str(time.time()) + os.path.splitext(data["file"])[1]

				os.rename(os.path.join(dst_path, path), os.path.join(settings.MEDIA_ROOT, new_name))
				
				data["file"] = new_name
			else:
				path = files.extract(data["file"], settings.MEDIA_ROOT)

		return data

	class Meta:
		model = PDFFile
		exclude = ('students', 'groups',)

	def create(self, data):
		topic = data['topic']

		pdf = None

		if not topic["id"] is None:
			if topic['id'] == "":
				topic_exist = Topic.objects.filter(subject = topic['subject'], name__unaccent__iexact = topic["name"])

				if topic_exist.exists():
					topic = topic_exist[0]
				else:
					topic = Topic.objects.create(name = topic['name'], subject = topic['subject'], repository = topic['repository'], visible = topic['visible'], order = topic['order'])
				
				data["topic"] = topic
			else:
				data["topic"] = get_object_or_404(Topic, id = topic["id"])


			f = open(os.path.join(settings.MEDIA_ROOT, data["file"]), encoding="latin-1")
			file = File(f)

			data["file"] = file

			pdf_data = data
			
			pendencies = pdf_data["pendencies_resource"]
			del pdf_data["pendencies_resource"]

			pdf = PDFFile()
			pdf.name = pdf_data["name"]
			pdf.brief_description = pdf_data["brief_description"]
			pdf.show_window = pdf_data["show_window"]
			pdf.all_students = pdf_data["all_students"]
			pdf.visible = pdf_data["visible"]
			pdf.order = pdf_data["order"]
			pdf.topic = pdf_data["topic"]
			pdf.file = pdf_data["file"]

			pdf.save()

			tags = data["tags"]

			for tag in tags:
				if tag["id"] == "":
					tag = Tag.objects.create(name = tag["name"])
				else:
					tag = get_object_or_404(Tag, id = tag["id"])

				pdf.tags.add(tag)
			
			resource = get_object_or_404(Resource, id = pdf.id)

			for pend in pendencies:
				Pendencies.objects.create(resource = resource, **pend)

		return pdf

	def update(self, instance, data):
		return instance

class CompletePDFFileSerializer(serializers.ModelSerializer):
	file = serializers.CharField(required = False, allow_blank = True)
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	groups = StudentsGroupSerializer(many = True)
	students = UserBackupSerializer(many = True)

	class Meta:
		model = PDFFile
		fields = '__all__'