from rest_framework import serializers

from .models import Topic, Resource

class TopicSerializer(serializers.ModelSerializer):
	class Meta:
		model = Topic
		exclude = ('subject',)