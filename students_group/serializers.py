from rest_framework import serializers

from users.serializers import UserBackupSerializer

from .models import StudentsGroup

class StudentsGroupSerializer(serializers.ModelSerializer):
	participants = UserBackupSerializer(many = True)

	class Meta:
		model = StudentsGroup
		fields = '__all__'
