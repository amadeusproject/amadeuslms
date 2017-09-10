import datetime
from django.db.models import Q

from rest_framework import serializers

from chat.models import ChatVisualizations

from .models import Subject, Tag

class TagSerializer(serializers.ModelSerializer):
	def validate(self, data):
		query = Tag.objects.filter(name = data['name'])
		
		if query.exists():
			data['id'] = query[0].id
		else:
			data['id'] = ""

		return data
	
	class Meta:
		model = Tag
		fields = '__all__'
		extra_kwargs = {
        	"name": {
	            "validators": [],
	        },
	    }
		validators = []

class SubjectSerializer(serializers.ModelSerializer):
	notifications = serializers.SerializerMethodField()

	def get_notifications(self, subject):
		user = self.context.get("request_user", None)

		if not user is None:
			return ChatVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & Q(message__subject = subject) & (Q(user__is_staff = True) | Q(message__subject__students = user) | Q(message__subject__professor = user) | Q(message__subject__category__coordinators = user))).distinct().count()
			
		return 0
	
	class Meta:
		model = Subject
		fields = ["name", "slug", "visible", "description_brief", "description", "notifications"]