from rest_framework import serializers
from .models import Course, Subject, Topic
from users.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
	#The set comes from the ManyToMany Relationship in django
	students = UserSerializer(many=True)
	professors = UserSerializer(many=True)
	category = serializers.ReadOnlyField(source ='category.name')
	class Meta:
		model = Course
		fields = ('name', 'slug', 'objectivies', 'content', 'max_students', 'create_date', 
			'init_register_date', 'end_register_date', 'init_date', 'end_date', 'public', 'category' ,'students', 'professors')

class SubjectSerializer(serializers.ModelSerializer):
	students = UserSerializer(many=True)
	professors = UserSerializer(many=True)
	course = serializers.ReadOnlyField(source='course.name')
	category = serializers.ReadOnlyField(source ='category.name')
	class Meta:
		model = Subject
		fields = ('name','slug','description','visible','init_date','course','category','professors','course','students')

class TopicSerializer(serializers.ModelSerializer):
	subject = serializers.ReadOnlyField(source='subject.name')
	owner = serializers.ReadOnlyField(source='owner.username')
	class Meta:
		model = Topic
		fields = ('name', 'slug','description','create_date','update_date','visible','owner','subject')


