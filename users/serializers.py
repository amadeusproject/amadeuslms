from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username','email','image','last_update','date_created','last_name','social_name',
			'is_staff','is_active','description')
