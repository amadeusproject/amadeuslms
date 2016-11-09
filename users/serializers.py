from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username','email','name','city','state','gender','image','birth_date','phone'
			'cpf','type_profile','titration','year_tritation','institution','curriculum','date_created',
			'is_staff','is_active')
