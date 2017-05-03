from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer
from pendencies.serializers import PendenciesSerializer
from students_group.serializers import StudentsGroupSerializer

from .models import YTVideo

class SimpleYTVideoSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)

	class Meta:
		model = YTVideo
		exclude = ('students', 'groups',)

class CompleteYTVideoSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	groups = StudentsGroupSerializer(many = True)

	class Meta:
		model = YTVideo
		fields = '__all__'