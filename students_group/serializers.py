from rest_framework import serializers

from users.serializers import UserBackupSerializer

from .models import StudentsGroup

class StudentsGroupSerializer(serializers.ModelSerializer):
	participants = UserBackupSerializer('get_files', many = True)

	def get_files(self, obj):
		files = self.context.get("files", None)

		return files

	class Meta:
		model = StudentsGroup
		fields = '__all__'
