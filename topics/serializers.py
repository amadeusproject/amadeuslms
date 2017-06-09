from rest_framework import serializers
from django.shortcuts import get_object_or_404

from subjects.models import Subject

from .models import Topic

class TopicSerializer(serializers.ModelSerializer):
	def validate(self, data):
		subject = self.context.get('subject', None)

		if subject:
			subject = get_object_or_404(Subject, slug = subject)
			topic = Topic.objects.filter(subject = subject, name__unaccent__iexact = data["name"])
			
			if topic.exists():
				data = topic[0].__dict__
			else:
				data["id"] = ""
				data["subject"] = subject
				data["order"] = Topic.objects.filter(subject = subject).count() + 1

				if data["repository"] == True:
					topic = Topic.objects.filter(subject = subject, repository = True)

					if topic.exists():
						data = topic[0].__dict__
				
		return data

	class Meta:
		model = Topic
		exclude = ('subject',)

