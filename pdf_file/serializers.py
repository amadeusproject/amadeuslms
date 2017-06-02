from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer
from pendencies.serializers import PendenciesSerializer
from students_group.serializers import StudentsGroupSerializer
from users.serializers import UserBackupSerializer

from .models import PDFFile

class SimplePDFFileSerializer(serializers.ModelSerializer):
	topic = TopicSerializer('get_subject')
	tags = TagSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	file = serializers.CharField(required = False, allow_blank = True, max_length = 255)

	def get_subject(self, obj):
		subject = self.context.get("subject", None)

		return subject

	def validate(self, data):
		files = self.context.get('files', None)

		if files:
			file_path = os.path.join(settings.MEDIA_ROOT, data["file_content"])

			if os.path.isfile(file_path):
				dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")

				path = files.extract(data["file_content"], dst_path)

				new_name = "files/file_" + str(time.time()) + os.path.splitext(data["file_content"])[1]

				os.rename(os.path.join(dst_path, path), os.path.join(settings.MEDIA_ROOT, new_name))
				
				data["file_content"] = new_name
			else:
				path = files.extract(data["file_content"], settings.MEDIA_ROOT)

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