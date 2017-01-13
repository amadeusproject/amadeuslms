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

def count_subjects(categories, user, all_subs = True):
	total = 0

	for category in categories:
		if not all_subs:
			for subject in category.subject_category.all():
				if user in subject.students.all() or user in subject.professor.all() or user in subject.category.coordinators.all():
					total += 1
		else:		
			total += category.subject_category.count()

	return total