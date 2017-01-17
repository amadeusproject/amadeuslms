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

	if user in subject.professor.all():
		return True

	if user in subject.category.coordinators.all():
		return True

	return False
