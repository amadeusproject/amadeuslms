from rest_framework import serializers

from log.serializers import LogSerializer
from log.models import Log

from .models import User

class UserBackupSerializer(serializers.ModelSerializer):
	log = LogSerializer(many = True, source = 'get_items')

	class Meta:
		model = User
		fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username','email','image','last_update','date_created','last_name','social_name',
			'is_staff','is_active','description')
