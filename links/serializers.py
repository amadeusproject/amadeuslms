from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer

from .models import Link

class SimpleLinkSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)

	class Meta:
		model = Link
		exclude = ('students', 'groups',)
