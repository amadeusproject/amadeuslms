from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer
from pendencies.serializers import PendenciesSerializer
from students_group.serializers import StudentsGroupSerializer
from users.serializers import UserBackupSerializer

from .models import Link

class SimpleLinkSerializer(serializers.ModelSerializer):
	topic = TopicSerializer('get_subject')
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)

	def get_subject(self, obj):
		subject = self.context.get("subject", None)

		return subject

	class Meta:
		model = Link
		exclude = ('students', 'groups',)

class CompleteLinkSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	groups = StudentsGroupSerializer(many = True)
	students = UserBackupSerializer(many = True)

	class Meta:
		model = Link
		fields = '__all__'