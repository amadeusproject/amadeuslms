from django import template

register = template.Library()

@register.filter(name = 'subject_count')
def subject_count(category, user):
	total = 0
	
	for subject in category.subject_category.all():
		if user in subject.students.all() or user in subject.professor.all() or user in subject.category.coordinators.all():
			total += 1

	return total