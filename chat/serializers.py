from rest_framework import serializers

from django.db.models import Q

from .models import TalkMessages, ChatFavorites

from subjects.serializers import SubjectSerializer
from users.serializers import UserSerializer

class ChatSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	subject = SubjectSerializer()
	favorite = serializers.SerializerMethodField()

	def get_favorite(self, message):
		user = self.context.get("request_user", None)

		if not user is None:
			return ChatFavorites.objects.filter(Q(user = user) & Q(message = message)).exists()

		return False

	class Meta:
		model = TalkMessages
		fields = ('text', 'user', 'subject', 'image_url', 'create_date', 'favorite')
