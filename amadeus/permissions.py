# File used to store functions to handle permissions

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
