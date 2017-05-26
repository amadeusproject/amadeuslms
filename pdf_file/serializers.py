from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer
from pendencies.serializers import PendenciesSerializer
from students_group.serializers import StudentsGroupSerializer
from users.serializers import UserBackupSerializer

from .models import PDFFile

class SimplePDFFileSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	file = serializers.CharField(required = False, allow_blank = True, max_length = 255)

	def validate(self, data):
		print(self.context)

		return data

	class Meta:
		model = PDFFile
		exclude = ('students', 'groups',)

class CompletePDFFileSerializer(serializers.ModelSerializer):
	file = serializers.CharField(required = False, allow_blank = True)
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	groups = StudentsGroupSerializer(many = True)
	students = UserBackupSerializer(many = True)

	class Meta:
		model = PDFFile
		fields = '__all__'