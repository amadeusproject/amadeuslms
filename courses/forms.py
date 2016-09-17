from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Category, Course, Subject, Topic


class CategoryForm(forms.ModelForm):

	class Meta:
		model = Category
		fields = ('name',)
		labels = {
			'name': _('Name')
		}
		help_texts = {
			'name': _('Category name')
		}


class CourseForm(forms.ModelForm):

	# init_register_date = forms.DateField(widget=forms.DateField)
	# end_register_date = forms.DateField(widget=forms.DateField)
	# init_date = forms.DateField(widget=forms.DateField)
	# end_date = forms.DateField(widget=forms.DateField)


	class Meta:
		model = Course
		fields = ('name', 'objectivies', 'content', 'max_students', 'init_register_date', 'end_register_date',
					'init_date', 'end_date', 'image', 'category',)
		labels = {
			'name': _('Name'),
			'objectivies': _('Objectives'),
			'content': _('Content'),
			'max_students': _('Number of studets maximum'),
			'init_register_date': _('Course registration start date'),
			'end_register_date': _('Course registration end date'),
			'init_date': _('Course start date'),
			'end_date': _('Course end date'),
			'image': _('Image'),
			'category': _('Category'),
		}
		help_texts = {
			'name': _('Course name'),
			'objectivies': _('Course objective'),
			'content': _('Course modules'),
			'max_students': _('Max number of students that a class can have'),
			'init_register_date': _('Date that starts the registration period of the course (dd/mm/yyyy)'),
			'end_register_date': _('Date that ends the registration period of the course (dd/mm/yyyy)'),
			'init_date': _('Date that the course starts (dd/mm/yyyy)'),
			'end_date': _('Date that the course ends (dd/mm/yyyy)'),
			'image': _('Representative image of the course'),
			'category': _('Category which the course belongs'),
		}

class SubjectForm(forms.ModelForm):

	class Meta:
		model = Subject
		fields = ('name', 'description', 'visible',)
		labels = {
			'name': _('Name'),
			'description': _('Description'),
			'visible': _('Is it visible?'),
		}
		help_texts = {
			'name': _("Subjects's name"),
			'description': _("Subjects's description"),
			'visible': _('Is the subject visible?'),
		}

class TopicForm(forms.ModelForm):

	class Meta:
		model = Topic
		fields = ('name', 'description',)
		labels = {
			'name': _('Name'),
			'description': _('Description'),
		}
		help_texts = {
			'name': _("Topic's name"),
			'description': _("Topic's description"),
		}
