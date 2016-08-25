from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Category, Course, Module

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
			'content': _('COurse modules'),
			'max_students': _('Max number of students that a class can have'),
			'init_register_date': _('Date that starts the registration period of the course (dd/mm/yyyy)'),
			'end_register_date': _('Date that ends the registration period of the course (dd/mm/yyyy)'),
			'init_date': _('Date that the course starts (dd/mm/yyyy)'),
			'end_date': _('Date that the course ends (dd/mm/yyyy)'),
			'image': _('Representative image of the course'),
			'category': _('Category which the course belongs'),
		}

class ModuleForm(forms.ModelForm):

	class Meta:
		model = Module
		fields = ('name', 'description', 'visible',)
		labels = {
			'name': _('Name'),
			'description': _('Description'),
			'visible': _('Is it visible?'),
		}
		help_texts = {
			'name': _("Module's name"),
			'description': _("Modules's description"),
			'visible': _('Is the module visible?'),	
		}