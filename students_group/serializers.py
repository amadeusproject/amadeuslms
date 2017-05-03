from rest_framework import serializers

from .models import StudentsGroup

class StudentsGroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = StudentsGroup
		fields = '__all__'
