from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer

from .models import FileLink

class SimpleFileLinkSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)

	class Meta:
		model = FileLink
		exclude = ('students', 'groups',)
