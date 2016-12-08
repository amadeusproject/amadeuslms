

from amadeus import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import CourseCategory, Course, Subject, Topic, ActivityFile, Activity, FileMaterial, LinkMaterial
from s3direct.widgets import S3DirectWidget
from django_summernote.widgets import SummernoteWidget

class CategoryCourseForm(forms.ModelForm):

	class Meta:
		model = CourseCategory
		fields = ('name',)
		labels = {
			'name': _('Name')
		}
		help_texts = {
			'name': _('CourseCategory name')
		}

class CourseForm(forms.ModelForm):
	
	class Meta:
		model = Course
		fields = ('name', 'category', 'coordenator','public')
		labels = {
			'name': _('Name'),
			'category': _('Category'),
			'coordenator': _('Coordenator'),
			'public':_('Public'),
		}
		help_texts = {
			'name': _('Course name'),
			'coordenator': _('Course Coordenator'),
			'public':_('To define if the course can be accessed by people not registered'),
		}
		widgets = {
			'category': forms.Select(),
			'coordenator': forms.Select(),
		}

class UpdateCourseForm(CourseForm):

	class Meta:
		model = Course
		fields = ('name', 'category', 'coordenator','public')
		labels = {
			'name': _('Name'),
			'category': _('Category'),
			'coordenator': _('Coordenator'),
			'public':_('Public'),
		}
		help_texts = {
			'name': _('Course name'),
			'coordenator': _('Course Coordenator'),
			'public':_('To define if the course can be accessed by people not registered'),
		}
		widgets = {
			'category': forms.Select(),
			'coordenator': forms.Select(),
		}

class SubjectForm(forms.ModelForm):
	init_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
	end_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
	def clean_end_date(self):
		end_date = self.cleaned_data['end_date']
		if('init_date' in self.cleaned_data):
			init_date = self.cleaned_data['init_date']
			if init_date and end_date and end_date < init_date:
				raise forms.ValidationError(_('The end date may not be before the start date.'))
		return end_date

	class Meta:
		
		model = Subject
		fields = ('name', 'description','init_date', 'end_date', 'visible',)
		localized_fields = ('init_date', 'end_date',)
		labels = {
			'name': _('Name'),
			'description': _('Description'),
			'init_date': _('Start date'),
			'end_date': _('End date'),
			'visible': _('Is it visible?'),
		}
		help_texts = {
			'name': _("Subjects's name"),
			'description': _("Subjects's description"),
			'init_date': _('Start date of the subject'),
			'end_date': _('End date of the subject'),
			'visible': _('Is the subject visible?'),
		}
		widgets = {
			'description':SummernoteWidget(),
		}

class TopicForm(forms.ModelForm):

	class Meta:
		model = Topic
		fields = ('name', 'description','visible')
		labels = {
			'name': _('Name'),
			'description': _('Description'),
			'visible': _('Is the topic visible?'),
		}
		help_texts = {
			'name': _("Topic's name"),
			'description': _("Topic's description"),
			'visible': _('Is it visible?'),
		}
		widgets = {
			'description':SummernoteWidget(),
		}

class ActivityFileForm(forms.ModelForm):
	name = forms.CharField(
		required=False,
		max_length=100,
		widget=forms.TextInput(attrs={
			'placeholder': 'Nome',
			'class': 'form-control'
	},))
	pdf = forms.URLField(required=True, widget=S3DirectWidget(
		dest='activitys',
		html=(
		'<div class="s3direct" data-policy-url="{policy_url}">'
		'  <a class="file-link" target="_blank" href="{file_url}">{file_name}</a>'
		'  <a class="file-remove" href="#remove">Remover</a>'
		'  <input class="file-url" type="hidden" value="{file_url}" id="{element_id}" name="{name}" />'
		'  <input class="file-dest" type="hidden" value="{dest}">'
		'  <input class="file-input" type="file" />'
		'  <div class="progress">'
		'    <div class="progress-bar progress-bar-success progress-bar-striped active bar">'
		'    </div>'
		'  </div>'
		'</div>'
	)))

	class Meta:
		model = ActivityFile
		fields = ['pdf','name']

class ActivityForm(forms.ModelForm):
	class Meta:
		model = Activity
		fields = ['topic', 'limit_date', 'students','all_students']

class FileMaterialForm(forms.ModelForm):
	class Meta:
		model = FileMaterial
		fields = ['name', 'file']

class LinkMaterialForm(forms.ModelForm):
	class Meta:
		model = LinkMaterial
		fields = ['material', 'name', 'description','url']


