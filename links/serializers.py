from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer
from pendencies.serializers import PendenciesSerializer
from students_group.serializers import StudentsGroupSerializer

from .models import Link

class SimpleLinkSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)

	class Meta:
		model = Link
		exclude = ('students', 'groups',)

class CompleteLinkSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	groups = StudentsGroupSerializer(many = True)

	class Meta:
		model = Link
		fields = '__all__'