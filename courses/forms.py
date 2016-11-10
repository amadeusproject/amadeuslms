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
	def clean_end_register_date(self):
		init_register_date = self.cleaned_data['init_register_date']
		end_register_date = self.cleaned_data['end_register_date']

		if init_register_date and end_register_date and end_register_date < init_register_date:
			raise forms.ValidationError(_('The end date may not be before the start date.'))
		return end_register_date

	def clean_init_date(self):
		end_register_date = self.cleaned_data['end_register_date']
		init_date = self.cleaned_data['init_date']

		if end_register_date and init_date and init_date <= end_register_date:
			raise forms.ValidationError(_('The course start date must be after the end of registration.'))
		return init_date

	def clean_end_date(self):
		init_date = self.cleaned_data['init_date']
		end_date = self.cleaned_data['end_date']

		if init_date and end_date and end_date < init_date:
			raise forms.ValidationError(_('The end date may not be before the start date.'))
		return end_date

	# init_register_date = forms.DateField(widget=forms.DateField)
	# end_register_date = forms.DateField(widget=forms.DateField)
	# init_date = forms.DateField(widget=forms.DateField)
	# end_date = forms.DateField(widget=forms.DateField)


	class Meta:
		model = Course
		fields = ('name', 'objectivies', 'content', 'max_students', 'init_register_date', 'end_register_date',
					'init_date', 'end_date', 'category', 'coordenator')
		labels = {
                            'name': _('Name'),
                            'objectivies': _('Objectives'),
                            'content': _('Content'),
                            'max_students': _('Number of studets maximum'),
                            'init_register_date': _('Course registration start date'),
                            'end_register_date': _('Course registration end date'),
                            'init_date': _('Course start date'),
                            'end_date': _('Course end date'),
                            'category': _('CourseCategory'),
                            'coordenator': _('Coordenator'),
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
                            'category': _('CourseCategory which the course belongs'),
                            'coordenator': _('Course Coordenator'),
		}

		widgets = {
                            'categoy': forms.Select(),
                            'coordenator': forms.Select(),
                            'objectivies': SummernoteWidget(attrs={'cols': 80, 'rows': 5}),
                            'content': SummernoteWidget(attrs={'cols': 80, 'rows': 5}),
		}

class UpdateCourseForm(CourseForm):
	def __init__(self, *args, **kwargs):
		super(UpdateCourseForm, self).__init__(*args, **kwargs)
		self.fields["students"].required = False

	class Meta:
		model = Course
		fields = ('name', 'objectivies', 'content', 'max_students', 'init_register_date', 'end_register_date',
					'init_date', 'end_date', 'category','students', 'coordenator')
		labels = {
                            'name': _('Name'),
                            'objectivies': _('Objectives'),
                            'content': _('Content'),
                            'max_students': _('Number of studets maximum'),
                            'init_register_date': _('Course registration start date'),
                            'end_register_date': _('Course registration end date'),
                            'init_date': _('Course start date'),
                            'end_date': _('Course end date'),
                            'category': _('CourseCategory'),
                            'coordenator': _('Coordenator'),
                            'students': _('Student'),
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
                            'category': _('CourseCategory which the course belongs'),
                            'coordenator': _('Course Coordenator'),
                            'students': _("Course's Students"),
		}
		widgets = {
                            'categoy': forms.Select(),
                            'coordenator': forms.Select(),
                            'objectivies': SummernoteWidget(attrs={'cols': 80, 'rows': 5}),
                            'content': SummernoteWidget(attrs={'cols': 80, 'rows': 5}),
		}

class SubjectForm(forms.ModelForm):

	class Meta:
		model = Subject
		fields = ('name', 'description','init_date', 'end_date', 'visible',)
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
		fields = ('name', 'description',)
		labels = {
			'name': _('Name'),
			'description': _('Description'),
		}
		help_texts = {
			'name': _("Topic's name"),
			'description': _("Topic's description"),
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
              },
            )
          )
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
