from rest_framework import serializers
from .models import Course, Subject, Topic
from users.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
	#The set comes from the ManyToMany Relationship in django
	class Meta:
		model = Course
		fields = ('name', 'category', 'coordenator','public')

class SubjectSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subject
		fields = ('name','slug','description','visible','init_date','course','category','professors','course','students')

class TopicSerializer(serializers.ModelSerializer):
	class Meta:
		model = Topic
		fields = ('name', 'slug','description','create_date','update_date','visible','owner','subject')
