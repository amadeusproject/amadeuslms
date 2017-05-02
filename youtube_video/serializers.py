from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer

from .models import YTVideo

class SimpleYTVideoSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)

	class Meta:
		model = YTVideo
		exclude = ('students', 'groups',)
