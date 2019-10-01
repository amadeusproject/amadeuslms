""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django import forms
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from subjects.models import Tag
from subjects.forms import ParticipantsMultipleChoiceField

from pendencies.forms import PendenciesLimitedForm
from pendencies.models import Pendencies

from .models import Questionary, Specification

class QuestionaryForm(forms.ModelForm):
    subject = None
    topic = None
    control_subject = forms.CharField(widget = forms.HiddenInput())

    students = ParticipantsMultipleChoiceField(queryset = None, required = False)

    def __init__(self, *args, **kwargs):
        super(QuestionaryForm, self).__init__(*args, **kwargs)
        self.subject = kwargs.get('initial').get('subject', None)
        self.topic = kwargs['initial'].get('topic', None)

        if self.instance.id:
            self.subject = self.instance.topic.subject
            self.topic = self.instance.topic
            self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))

        self.initial['control_subject'] = self.subject.id
        self.fields['students'].queryset = self.subject.students.all()
        self.fields['groups'].queryset = self.subject.group_subject.all()

    tags = forms.CharField(label = _('Tags'), required = False)

    class Meta:
        model = Questionary
        fields = ['name', 'presentation', 'data_ini', 'data_end', 'brief_description','show_window', 'all_students', 'students', 'groups', 'visible']
        labels = {
            'name': _('Questionary Name'),
        }
        widgets = {
            'presentation': forms.Textarea,
            'brief_description': forms.Textarea,
            'students': forms.SelectMultiple,
            'groups': forms.SelectMultiple,
        }

    def clean(self):
        cleaned_data = super(QuestionaryForm, self).clean()

        data_ini = cleaned_data.get('data_ini', None)
        data_end = cleaned_data.get('data_end', None)
        name = cleaned_data.get('name', '')
        
        if self.topic:
            if self.instance.id:
                same_name = self.topic.resource_topic.filter(name__iexact = name).exclude(id = self.instance.id).count()
            else:
                same_name = self.topic.resource_topic.filter(name__iexact = name).count()

            if same_name > 0:
                self.add_error('name', _('This subject already has a questionary with this name'))
        
        if data_ini:
            if not data_ini == ValueError:
                if not self.instance.id and data_ini.date() < datetime.today().date():
                    self.add_error('data_ini', _("This input should be filled with a date equal or after today's date."))

                if data_ini.date() < self.subject.init_date:
                    self.add_error('data_ini', _('This input should be filled with a date equal or after the subject begin date.("%s")')%(self.subject.init_date))

                if data_ini.date() > self.subject.end_date:
                    self.add_error('data_ini', _('This input should be filled with a date equal or before the subject end date.("%s")')%(self.subject.end_date))
        else:
            self.add_error('data_ini', _('This field is required'))

        if data_end:
            if not data_end == ValueError:
                if not self.instance.id and data_end.date() < datetime.today().date():
                    self.add_error('data_end', _("This input should be filled with a date equal or after today's date."))

                if data_end.date() < self.subject.init_date:
                    self.add_error('data_end', _('This input should be filled with a date equal or after the subject begin date.("%s")')%(self.subject.init_date))

                if data_end.date() > self.subject.end_date:
                    self.add_error('data_end', _('This input should be filled with a date equal or before the subject end date.("%s")')%(self.subject.end_date))

                if not data_ini == ValueError and data_ini and data_end < data_ini:
                    self.add_error('data_end', _("This input should be filled with a date equal or before the date stabilished for the init."))
        else:
            self.add_error('data_end', _('This field is required'))

        return cleaned_data

    def save(self, commit = True):
        super(QuestionaryForm, self).save(commit = True)

        self.instance.save()

        previous_tags = self.instance.tags.all()

        tags = self.cleaned_data['tags'].split(",")

        #Excluding unwanted tags
        for prev in previous_tags:
            if not prev.name in tags:
                self.instance.tags.remove(prev)

        for tag in tags:
            tag = tag.strip()

            exist = Tag.objects.filter(name = tag).exists()

            if exist:
                new_tag = Tag.objects.get(name = tag)
            else:
                new_tag = Tag.objects.create(name = tag)

            if not new_tag in self.instance.tags.all():
                self.instance.tags.add(new_tag)

        return self.instance

class SpecificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SpecificationForm, self).__init__(*args, **kwargs)

        if kwargs.get('initial', None):
            self.subject = kwargs.get('initial').get('subject', None)
            self.subject = self.subject.id
        elif self.instance.id:
            self.subject = self.instance.questionary.topic.subject
            self.subject = self.subject.id
        else:
            self.subject = kwargs['data'].get('control_subject')

        self.fields['categories'].queryset = Tag.objects.filter(question_categories__subject__id = self.subject).distinct()

    class Meta:
        model = Specification
        fields = ['categories', 'n_questions']
        widgets = {
            'categories': forms.SelectMultiple,
            'n_questions': forms.Select,
        }

    def clean(self):
        cleaned_data = super(SpecificationForm, self).clean()

        categories = cleaned_data.get('categories', None)
        n_questions = cleaned_data.get('n_questions', None)

        if categories and (not n_questions or n_questions == ''):
            self.add_error('n_questions', _('You must provide the number of questions for the combination.'))

        if n_questions and n_questions == "0":
            self.add_error('n_questions', _('There is no questions for this combination of categories. Please try another combination.'))

        return cleaned_data

class SpecificationFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(SpecificationFormset, self).__init__(*args, **kwargs)

        self.forms[0].empty_permitted = False

    def clean(self):
        n_questions = self.forms[0].cleaned_data.get('n_questions', None)

        if not n_questions:
            raise forms.ValidationError(_('It\'s necessary to enter at least one question specification.'))

InlinePendenciesFormset = inlineformset_factory(Questionary, Pendencies, form = PendenciesLimitedForm, extra = 1, max_num = 3, validate_max = True, can_delete = True)
InlineSpecificationFormset = inlineformset_factory(Questionary, Specification, form = SpecificationForm, min_num = 1, validate_min = True, extra = 0, can_delete = True, formset = SpecificationFormset)