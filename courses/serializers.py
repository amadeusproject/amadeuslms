from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
	class Meta:
		model = Course
		fields = ['id', 'name', 'slug', 'objectives', 'content', 'init_date', 'end_date', 'init_register_date', 'end_register_date', 'image', 'max_students', 'category']