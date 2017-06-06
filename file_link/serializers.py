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

from .models import FileLink

class SimpleFileLinkSerializer(serializers.ModelSerializer):
	topic = TopicSerializer('get_subject')
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	file_content = serializers.CharField(required = False, allow_blank = True, max_length = 255)

	def get_subject(self, obj):
		subject = self.context.get("subject", None)

		return subject

	def validate(self, data):
		files = self.context.get('files', None)

		if files:
			file_path = os.path.join(settings.MEDIA_ROOT, data["file_content"])

			if os.path.isfile(file_path):
				dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")

				path = files.extract(data["file_content"], dst_path)

				new_name = "files/file_" + str(time.time()) + os.path.splitext(data["file_content"])[1]

				os.rename(os.path.join(dst_path, path), os.path.join(settings.MEDIA_ROOT, new_name))
				
				data["file_content"] = new_name
			else:
				path = files.extract(data["file_content"], settings.MEDIA_ROOT)

		return data

	class Meta:
		model = FileLink
		extra_kwargs = {
        	"file_content": {
        		"required": False,
	            "validators": [],
	        },
	    }
		exclude = ('students', 'groups',)
		validators = []

	def create(self, data):
		topic = data['topic']

		file_link = None

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


			f = open(os.path.join(settings.MEDIA_ROOT, data["file_content"]), encoding="latin-1")
			file = File(f)

			data["file_content"] = file

			file_link_data = data
			
			pendencies = file_link_data["pendencies_resource"]
			del file_link_data["pendencies_resource"]

			file_link = FileLink()
			file_link.name = file_link_data["name"]
			file_link.brief_description = file_link_data["brief_description"]
			file_link.show_window = file_link_data["show_window"]
			file_link.all_students = file_link_data["all_students"]
			file_link.visible = file_link_data["visible"]
			file_link.order = file_link_data["order"]
			file_link.topic = file_link_data["topic"]
			file_link.file_content = file_link_data["file_content"]

			file_link.save()
			
			tags = data["tags"]

			for tag in tags:
				if tag["id"] == "":
					tag = Tag.objects.create(name = tag["name"])
				else:
					tag = get_object_or_404(Tag, id = tag["id"])

				file_link.tags.add(tag)
			
			resource = get_object_or_404(Resource, id = file_link.id)

			for pend in pendencies:
				Pendencies.objects.create(resource = resource, **pend)

		return file_link

	def update(self, instance, data):
		return instance

class CompleteFileLinkSerializer(serializers.ModelSerializer):
	file_content = serializers.CharField(required = False, allow_blank = True)
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	groups = StudentsGroupSerializer(many = True)
	students = UserBackupSerializer(many = True)

	class Meta:
		model = FileLink
		fields = '__all__'
