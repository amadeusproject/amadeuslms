from rest_framework import serializers
from .models import Course, Subject, Topic

class CourseSerializer(serializers.ModelSerializer):
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


