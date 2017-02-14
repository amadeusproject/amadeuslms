from django.db.models import Q

from users.models import User

def getSpaceUsers(user, post):
	if post._my_subclass == "generalpost":
		return User.objects.all().exclude(id = user)
	elif post._my_subclass == "categorypost":
		space = post.get_space()

		return User.objects.filter(Q(is_staff = True) | Q(coordinators__id = space) | Q(professors__category__id = space) | Q(subject_student__category__id = space)).exclude(id = user)

	return None