from django.utils import timezone

from users.models import User

from .models import GoalItem, MyGoals

def set_goals():
	specifications = GoalItem.objects.filter(goal__limit_submission_date__date = timezone.now())
	entries = []

	for goal in specifications:
		users = User.objects.filter(subject_student = goal.goal.topic.subject)

		for user in users:
			if not MyGoals.objects.filter(user = user, item = goal).exists():
				entries.append(MyGoals(user = user, item = goal, value = goal.ref_value))

	MyGoals.objects.bulk_create(entries)
