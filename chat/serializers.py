from rest_framework import serializers

from .models import TalkMessages

from subjects.serializers import SubjectSerializer
from users.serializers import UserSerializer

class ChatSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	subject = SubjectSerializer()
	image = serializers.CharField(required = False, allow_blank = True, max_length = 255)

	class Meta:
		model = TalkMessages
		exclude = ["talk"]