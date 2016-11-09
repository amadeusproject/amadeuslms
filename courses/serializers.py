from rest_framework import serializers
from .models import Course, Subject, Topic
from users.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
	#The set comes from the ManyToMany Relationship in django
	students = UserSerializer(source='courses_student')
	professors = UserSerializer(source='courses_professors')
	class Meta:
		model = Course
		fields = ('name', 'slug', 'objectivies', 'content, max_students', 'create_date', 
			'init_register_date', 'end_register_date', 'init_date', 'end_date', 'public')

class SubjectSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subject
		fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
	class Meta:
		model = Topic


