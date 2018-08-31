""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

# coding=utf-8
from django import forms
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _

from resubmit.widgets import ResubmitFileWidget

from subjects.models import Tag

from .models import Question, Alternative

class QuestionForm(forms.ModelForm):
    subject = None
    MAX_UPLOAD_SIZE = 5*1024*1024

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        
        if not kwargs['instance'] is None:
            self.initial['categories'] = ", ".join(self.instance.categories.all().values_list("name", flat = True))

    def clean_file(self):
        file = self.cleaned_data.get('question_img', False)

        if file:
            if hasattr(file, '_size'):
                if file._size > self.MAX_UPLOAD_SIZE:
                    self._errors['file'] = [_("The file is too large. It should have less than 5MB.")]

                    return ValueError

        return file

    categories = forms.CharField(label = _('Categories *'), required = True)

    class Meta:
        model = Question
        fields = ['enunciado', 'question_img']
        widgets = {
            'enunciado': forms.Textarea,
            'question_img': ResubmitFileWidget(attrs={'accept':'image/*'}),
        }

    def save(self, commit=True):
        super(QuestionForm, self).save(commit = True)

        self.instance.save()

        previous_cats = self.instance.categories.all()

        categories = self.cleaned_data['categories'].split(',')

        for prev in previous_cats:
            if not prev.name in categories:
                self.instance.categories.remove(prev)

        for cat in categories:
            cat = cat.strip()

            exist = Tag.objects.filter(name = cat).exists()

            if exist:
                new_cat = Tag.objects.get(name = cat)
            else:
                new_cat = Tag.objects.create(name = cat)

            if not new_cat in self.instance.categories.all():
                self.instance.categories.add(new_cat)

        return self.instance

class AlternativeForm(forms.ModelForm):
    MAX_UPLOAD_SIZE = 10*1024*1024

    def clean_file(self):
        file = self.cleaned_data.get('alt_img', False)

        if file:
            if hasattr(file, '_size'):
                if file._size > self.MAX_UPLOAD_SIZE:
                    self._errors['file'] = [_("The file is too large. It should have less than 5MB.")]

                    return ValueError

        return file

    class Meta:
        model = Alternative
        fields = ['content', 'alt_img', 'is_correct']
        widgets = {
            'content': forms.Textarea,
            'alt_img': ResubmitFileWidget(attrs={'accept':'image/*'}),
        }

BaseAlternativeFormset = modelformset_factory(Alternative, form = AlternativeForm, extra = 4, max_num = 4, min_num = 4)

class AlternativeFormset(BaseAlternativeFormset):
    def __init__(self, *args, **kwargs):
        super(AlternativeFormset, self).__init__(*args, **kwargs)

    def clean(self):
        if any(self.errors):
            return

        contents = []
        duplicates = False
        has_correct = False

        for form in self.forms:
            content = form.cleaned_data['content']
            is_correct = form.cleaned_data['is_correct']

            if content:
                if content in contents:
                    duplicates = True

                contents.append(content)

                if duplicates:
                    raise forms.ValidationError(_("The alternatives must not be equals."), code = 'duplicate_alternatives')

                if has_correct:
                    if is_correct is True:
                        raise forms.ValidationError(_("Only one alternative must be correct."), code = 'multiple_correct')
                    else:
                        has_correct = True
                else:
                    if is_correct is True:
                        has_correct = True