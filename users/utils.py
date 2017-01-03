#    File used to store useful user functions    #

from categories.models import Category
from subjects.models import Subject

def has_dependencies(user):
	if user.is_staff: #Check admin function
		return True

	cats = Category.objects.filter(coordinators = user)

	if len(cats) > 0: #Check coordinator function
		return True

	subs = Subject.objects.filter(professor = user)

	if len(subs) > 0: #Check professor function
		return True

	subs = Subject.objects.filter(students = user)

	if len(subs) > 0: #Check student function
		return True

	return False