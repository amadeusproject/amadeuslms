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

from .models import Webpage

class SimpleWebpageSerializer(serializers.ModelSerializer):
	topic = TopicSerializer('get_subject')
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)

	def get_subject(self, obj):
		subject = self.context.get("subject", None)

		return subject

	class Meta:
		model = Webpage
		exclude = ('students', 'groups',)

	def create(self, data):
		topic = data['topic']

		webpage = None

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
						topic = Topic.objects.create(name = topic['name'], subject = topic['subject'], repository = topic['repository'], visible = topic['visible'], order = topic['order'])
					
					data["topic"] = topic
				else:
					data["topic"] = get_object_or_404(Topic, id = topic["id"])

				webpage_data = data
				
				pendencies = webpage_data["pendencies_resource"]
				del webpage_data["pendencies_resource"]

				webpage = Webpage()
				webpage.name = webpage_data["name"]
				webpage.brief_description = webpage_data["brief_description"]
				webpage.show_window = webpage_data["show_window"]
				webpage.all_students = webpage_data["all_students"]
				webpage.visible = webpage_data["visible"]
				webpage.order = webpage_data["order"]
				webpage.topic = webpage_data["topic"]
				webpage.content = webpage_data["content"]

				webpage.save()

				tags = data["tags"]

				for tag in tags:
					if tag["id"] == "":
						tag = Tag.objects.create(name = tag["name"])
					else:
						tag = get_object_or_404(Tag, id = tag["id"])

					webpage.tags.add(tag)

				resource = get_object_or_404(Resource, id = webpage.id)

				for pend in pendencies:
					Pendencies.objects.create(resource = resource, **pend)

		return webpage

	def update(self, instance, data):
		return instance

class CompleteWebpageSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	groups = StudentsGroupSerializer(many = True)
	students = UserBackupSerializer(many = True)

	class Meta:
		model = Webpage
		fields = '__all__'