from rest_framework import serializers
from django.shortcuts import get_object_or_404

from subjects.serializers import TagSerializer
from topics.serializers import TopicSerializer
from pendencies.serializers import PendenciesSerializer
from students_group.serializers import StudentsGroupSerializer
from users.serializers import UserBackupSerializer

from subjects.models import Tag
from topics.models import Topic, Resource
from pendencies.models import Pendencies

from .models import Goals, GoalItem

class GoalItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = GoalItem
		exclude = ('goal',)

class SimpleGoalSerializer(serializers.ModelSerializer):
	topic = TopicSerializer('get_subject')
	tags = TagSerializer(many = True)
	item_goal = GoalItemSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)

	def get_subject(self, obj):
		subject = self.context.get("subject", None)

		return subject

	class Meta:
		model = Goals
		exclude = ('students', 'groups',)

	def create(self, data):
		topic = data['topic']

		goals = None

		if not topic["id"] is None:
			if "subject" in topic:
				r_exits = Resource.objects.filter(topic__subject = topic["subject"], name__unaccent__iexact = data["name"])
			else:
				r_exits = Resource.objects.filter(topic__subject__id = topic["subject_id"], name__unaccent__iexact = data["name"])

			if not r_exits.exists():
				if topic['id'] == "":
					topic_exist = Topic.objects.filter(subject = topic['subject'], name__unaccent__iexact = topic["name"])

					if topic_exist.exists():
						topic = topic_exist[0]
					else:
						topic = Topic.objects.create(name = topic['name'], subject = topic['subject'], repository = topic['repository'], visible = topic['visible'], order = topic['order'])
					
					data["topic"] = topic
				else:
					data["topic"] = get_object_or_404(Topic, id = topic["id"])

				goals_data = data
				
				pendencies = goals_data["pendencies_resource"]
				del goals_data["pendencies_resource"]

				goal_items = goals_data["item_goal"]
				del goals_data["item_goal"]

				goals = Goals()
				goals.name = goals_data["name"]
				goals.brief_description = goals_data["brief_description"]
				goals.show_window = goals_data["show_window"]
				goals.all_students = goals_data["all_students"]
				goals.visible = goals_data["visible"]
				goals.order = goals_data["order"]
				goals.topic = goals_data["topic"]
				goals.presentation = goals_data["presentation"]
				goals.limit_submission_date = goals_data["limit_submission_date"]

				goals.save()
				
				tags = data["tags"]

				for tag in tags:
					if tag["id"] == "":
						tag = Tag.objects.create(name = tag["name"])
					else:
						tag = get_object_or_404(Tag, id = tag["id"])

					goals.tags.add(tag)

				resource = get_object_or_404(Resource, id = goals.id)

				for item in goal_items:
					GoalItem.objects.create(goal = goals, **item)

				for pend in pendencies:
					Pendencies.objects.create(resource = resource, **pend)

		return goals

	def update(self, instance, data):
		return instance

class CompleteGoalSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	tags = TagSerializer(many = True)
	item_goal = GoalItemSerializer(many = True)
	pendencies_resource = PendenciesSerializer(many = True)
	groups = StudentsGroupSerializer(many = True)
	students = UserBackupSerializer(many = True)

	class Meta:
		model = Goals
		fields = '__all__'