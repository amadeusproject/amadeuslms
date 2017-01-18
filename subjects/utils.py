
#    File used to store useful subject functions    #
from categories.models import Category
from .models import Subject
from django.db.models import Q

def has_student_profile(user, category):
	for subject in category.subject_category.all():
		if subject.students.filter(id = user.id).exists() and subject.visible:
			return True

	return False

def has_professor_profile(user, category):
	for subject in category.subject_category.all():
		if subject.professor.filter(id = user.id).exists() and subject.visible:
			return True

	return False

def count_subjects( user, all_subs = True):
	total = 0
	pk = user.pk

	"""for category in categories:
		if not all_subs:
			for subject in category.subject_category.all():
				if user in subject.students.all() or user in subject.professor.all() or user in subject.category.coordinators.all():
					total += 1
		else:		
			total += category.subject_category.count()"""
	if all_subs:
		#total += Category.objects.filter(Q(coordinators__pk = pk) | Q(visible=True) ).distinct().count()
		total = Subject.objects.filter(Q(students__pk=pk) | Q(professor__pk=pk) | Q(category__coordinators__pk=pk) | Q(visible = True)).distinct().count()
	else:
		
		total = Subject.objects.filter(Q(students__pk=pk) | Q(professor__pk=pk) | Q(category__coordinators__pk=pk)).distinct().count()
	return total