from rest_framework import serializers

from .models import Topic

class TopicSerializer(serializers.ModelSerializer):
	def validate(self, data):
		subject = self.context.get('subject', None)

		if subject:
			print(subject)

		return data

	class Meta:
		model = Topic
		exclude = ('subject',)

