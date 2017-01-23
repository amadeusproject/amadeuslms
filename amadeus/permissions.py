# File used to store functions to handle permissions

from topics.models import Resource

"""
	Function to know if a user has permission to:
		- Edit Subject
		- Delete Subject
		- Create Topic inside Subject 
"""
def has_subject_permissions(user, subject):
	if user.is_staff:
		return True

	if subject.professor.filter(id = user.id).exists():
		return True

	if subject.category.coordinators.filter(id = user.id).exists():
		return True

	return False

"""
	Function to know if user has permission to:
		- Access Resource
"""
def has_resource_permissions(user, resource):
	if has_subject_permissions(user, resource.topic.subject):
		return True

	if resource.visible or resource.topic.repository:
		if resource.all_students:
			if subject.students.filter(id = user.id).exists():
				return True

		if resource.students.filter(id = user.id).exists():
			return True

		if Resource.objects.filter(id = resource.id, groups__participants__pk = user.pk).exists():
			return True

	return False




