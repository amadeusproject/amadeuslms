from rest_framework import serializers

from .models import TalkMessages

from subjects.serializers import SubjectSerializer
from users.serializers import UserSerializer

class ChatSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	subject = SubjectSerializer()

	class Meta:
		model = TalkMessages
		fields = ('text', 'user', 'subject', 'image_url', 'create_date', )
