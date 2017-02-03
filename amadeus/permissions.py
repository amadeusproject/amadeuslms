# File used to store functions to handle permissions

from categories.models import Category
from subjects.models import Subject
from topics.models import Resource

"""
	Function to know if a user has permission to:
		- Edit Category
		- Delete Category
		- Create Subject
		- Replicate Subject
"""
def has_category_permissions(user, category):
	if user.is_staff:
		return True

	if category.coordinators.filter(id = user.id).exists():
		return True

	return False

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
		- See subject
"""
def has_subject_view_permissions(user, subject):
	if has_subject_permissions(user, subject):
		return True

	if subject.students.filter(id = user.id).exists():
		return True

	return False

"""
	Function to know if user is student of some subject in category
"""
def has_category_permission(user, cat_slug):
	exist = Subject.objects.filter(students__id = user.id, category__slug = cat_slug).exists()

	return exist

"""
	Function to know if user has permission to:
		- Access Resource
"""
def has_resource_permissions(user, resource):
	if has_subject_permissions(user, resource.topic.subject):
		return True

	if resource.visible or resource.topic.repository:
		if resource.all_students:
			if resource.topic.subject.students.filter(id = user.id).exists():
				return True

		if resource.students.filter(id = user.id).exists():
			return True

		if Resource.objects.filter(id = resource.id, groups__participants__pk = user.pk).exists():
			return True

	return False




