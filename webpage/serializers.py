from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer

from .models import Webpage

class SimpleWebpageSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)

	class Meta:
		model = Webpage
		exclude = ('students', 'groups',)
