""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
import datetime

from users.models import User

from .models import Subject, Tag


class ParticipantsMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        label = str(obj) + " - (" + obj.email + ")"

        return label

class CreateSubjectForm(forms.ModelForm):
    category_id = None

    students = ParticipantsMultipleChoiceField(queryset = User.objects.all(), required = False)
    professor = ParticipantsMultipleChoiceField(queryset = User.objects.all(), required = False)

    def __init__(self, *args, **kwargs):
        super(CreateSubjectForm, self).__init__(*args, **kwargs)

        if kwargs['initial']:
            if kwargs['initial']['category']:
                categories = kwargs['initial']['category']

                if categories.count() > 0:
                    self.category_id = categories[0].id


        if not kwargs['instance'] is None:
            self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))

    # TODO: Define form fields here
    tags = forms.CharField(label = _('Tags'), required = False)

    class Meta:
        model = Subject

        fields = ('name', 'description_brief', 'description', 'subscribe_begin', 'subscribe_end', 'init_date', 'end_date',
         'visible', 'professor', 'students', )


        widgets = {
            'description_brief': forms.Textarea,
            'description': forms.Textarea,
            'professor': forms.SelectMultiple,
            'students': forms.SelectMultiple,
        }

    def save(self, commit=True):
        super(CreateSubjectForm, self).save(commit = True)

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

    def clean_name(self):
        name = self.cleaned_data.get('name')
        
        if self.instance.id:
            same_name = Subject.objects.filter(name__unaccent__iexact = name, category = self.category_id).exclude(id = self.instance.id)
        else:
            same_name = Subject.objects.filter(name__unaccent__iexact = name, category = self.category_id)
        
        if same_name.count() > 0:
            self._errors['name'] = [_('There is another subject with this name, try another one.')]
            return ValueError
        
        return name

    def clean_subscribe_begin(self):
        subscribe_begin = self.cleaned_data['subscribe_begin']

        if subscribe_begin < datetime.datetime.today().date():
            self._errors['subscribe_begin'] = [_('This date must be today or after')]
            return ValueError

        return subscribe_begin

    def clean_subscribe_end(self):
        subscribe_end = self.cleaned_data['subscribe_end']
        subscribe_begin =  self.cleaned_data['subscribe_begin']

        if subscribe_begin is ValueError or subscribe_end < subscribe_begin:
            self._errors['subscribe_end'] = [_('This date must be equal subscribe begin or after')]
            return ValueError
        return subscribe_end

    def clean_init_date(self):
        init_date = self.cleaned_data['init_date']
        subscribe_end = self.cleaned_data['subscribe_end']


        if subscribe_end is ValueError or init_date <= subscribe_end:
            self._errors['init_date'] = [_('This date must be after subscribe end')]
            return ValueError
        return init_date

    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        init_date = self.cleaned_data['init_date']

        if init_date is ValueError or end_date < init_date:
            self._errors['end_date'] = [_('This date must be equal init date or after')]
            return ValueError
        return end_date

class UpdateSubjectForm(forms.ModelForm):
    students = ParticipantsMultipleChoiceField(queryset = User.objects.all(), required = False)
    professor = ParticipantsMultipleChoiceField(queryset = User.objects.all(), required = False)

    def __init__(self, *args, **kwargs):
        super(UpdateSubjectForm, self).__init__(*args, **kwargs)

        if not kwargs['instance'] is None:
            self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))

    # TODO: Define form fields here
    tags = forms.CharField(label = _('Tags'), required = False)

    class Meta:
        model = Subject

        fields = ('name', 'description_brief', 'description', 'subscribe_begin', 'subscribe_end', 'init_date', 'end_date',
         'visible', 'professor', 'students',  )


        widgets = {
            'description_brief': forms.Textarea,
            'description': forms.Textarea,
            'professor': forms.SelectMultiple,
            'students': forms.SelectMultiple,
        }

    def save(self, commit=True):
        super(UpdateSubjectForm, self).save(commit = True)

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

    def clean_name(self):
        name = self.cleaned_data.get('name')
        categoria = self.instance.category
        
        if self.instance.id:
            same_name = Subject.objects.filter(name__unaccent__iexact = name , category = categoria).exclude(id = self.instance.id)
        else:
            same_name = Subject.objects.filter(name__unaccent__iexact = name, category = categoria)
        
        if same_name.count() > 0:
            self._errors['name'] = [_('There is another subject with this name, try another one.')]

        return name

    # def clean_subscribe_begin(self):
    #     subscribe_begin = self.cleaned_data['subscribe_begin']
    #
    #     if subscribe_begin < datetime.datetime.today().date() and subscribe_begin < self.instance.subscribe_begin:
    #         self._errors['subscribe_begin'] = [_('This date must be today or after')]
    #         return ValueError
    #
    #     return subscribe_begin

    def clean_subscribe_end(self):
        subscribe_end = self.cleaned_data['subscribe_end']
        subscribe_begin =  self.cleaned_data['subscribe_begin']

        if subscribe_begin is ValueError or subscribe_end < subscribe_begin:
            self._errors['subscribe_end'] = [_('This date must be equal subscribe begin or after')]
            return ValueError
        return subscribe_end

    def clean_init_date(self):
        init_date = self.cleaned_data['init_date']
        subscribe_end = self.cleaned_data['subscribe_end']


        if subscribe_end is ValueError or init_date <= subscribe_end:
            self._errors['init_date'] = [_('This date must be after subscribe end')]
            return ValueError
        return init_date

    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        init_date = self.cleaned_data['init_date']

        if init_date is ValueError or end_date < init_date:
            self._errors['end_date'] = [_('This date must be equal init date or after')]
            return ValueError
        return end_date


class CreateTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name',)
