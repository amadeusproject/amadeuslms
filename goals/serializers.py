from rest_framework import serializers

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer

from .models import Goals, GoalItem

class GoalItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = GoalItem
		exclude = ('goal',)

class SimpleGoalSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	item_goal = GoalItemSerializer(many = True)

	class Meta:
		model = Goals
		exclude = ('students', 'groups',)
