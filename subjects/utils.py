#    File used to store useful subject functions    #

def has_student_profile(user, category):
	for subject in category.subject_category.all():
		if user in subject.students.all():
			return True

	return False

def has_professor_profile(user, category):
	for subject in category.subject_category.all():
		if user in subject.professor.all():
			return True

	return False

def count_subjects(categories):
	total = 0

	for category in categories:
		total += category.subject_category.count()

	return total