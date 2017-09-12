from django.db.models import Q

from users.models import User

def getSpaceUsers(user, post):
	if post._my_subclass == "generalpost":
		return User.objects.all().exclude(id = user)
	elif post._my_subclass == "categorypost":
		space = post.get_space()

		return User.objects.filter(Q(is_staff = True) | Q(coordinators__id = space) | Q(professors__category__id = space) | Q(subject_student__category__id = space)).exclude(id = user).distinct()
	elif post._my_subclass == "subjectpost":
		space = post.get_space()

		if post.subjectpost.resource:
			resource = post.subjectpost.resource

			return User.objects.filter(Q(is_staff = True) | Q(professors__id = space) | Q(coordinators__subject_category__id = space) | Q(resource_students = resource) | Q(group_participants__resource_groups = resource) | (Q(subject_student__id = space) & Q(subject_student__topic_subject__resource_topic = resource) & Q(subject_student__topic_subject__resource_topic__all_students = True))).exclude(id = user).distinct()
		else:
			return User.objects.filter(Q(is_staff = True) | Q(professors__id = space) | Q(coordinators__subject_category__id = space) | Q(subject_student__id = space)).exclude(id = user).distinct()

	return None