""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.forms.models import inlineformset_factory

from subjects.models import Tag

from .models import Bulletin

from resubmit.widgets import ResubmitFileWidget

from pendencies.forms import PendenciesLimitedForm
from pendencies.models import Pendencies

class BulletinForm(forms.ModelForm):
    subject = None
    MAX_UPLOAD_SIZE = 1024*1024

    def __init__(self, *args, **kwargs):
        super(BulletinForm, self).__init__(*args, **kwargs)

        self.subject = kwargs['initial'].get('subject', None)

        if self.instance.id:
            self.subject = self.instance.topic.subject
            self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))


    tags = forms.CharField(label = _('Tags'), required = False)

    class Meta:
        model = Bulletin
        fields = ['name', 'content', 'brief_description',  'show_window', 'visible','file_content','indicators']
        labels = {
            'name': _('Bulletin name'),
            'content': _('Bulletin content'),
        }
        widgets = {
            'content': forms.Textarea,
            'brief_description': forms.Textarea,
            'file_content': ResubmitFileWidget(attrs={'accept':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/vnd.oasis.opendocument.spreadsheet,text/csv'}),
            'indicators': ResubmitFileWidget(attrs={'accept':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/vnd.oasis.opendocument.spreadsheet,text/csv'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '')

        topics = self.subject.topic_subject.all()

        for topic in topics:
            if self.instance.id:
                same_name = topic.resource_topic.filter(name__unaccent__iexact = name).exclude(id = self.instance.id).count()
            else:
                same_name = topic.resource_topic.filter(name__unaccent__iexact = name).count()

            if same_name > 0:
                self._errors['name'] = [_('This subject already has a bulletin with this name')]

                return ValueError

        return name


    def clean_file_content(self):
        file_content = self.cleaned_data.get('file_content', False)

        if file_content:
        	if hasattr(file_content, '_size'):
        		if file_content._size > self.MAX_UPLOAD_SIZE:
        			self._errors['file_content'] = [_("The file is too large. It should have less than 1MB.")]

        			return ValueError

        elif not self.instance.pk:
        	self._errors['file_content'] = [_('This field is required.')]

        	return ValueError

        return file_content

    def clean_indicators(self):
        indicators = self.cleaned_data.get('indicators', False)

        if indicators:
        	if hasattr(indicators, '_size'):
        		if indicators._size > self.MAX_UPLOAD_SIZE:
        			self._errors['indicators'] = [_("The file is too large. It should have less than 1MB.")]

        			return ValueError

        elif not self.instance.pk:
        	self._errors['indicators'] = [_('This field is required.')]

        	return ValueError

        return indicators

    def save(self, commit = True):
        super(BulletinForm, self).save(commit = True)

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

class FormModalMessage(forms.Form):
    MAX_UPLOAD_SIZE = 5*1024*1024

    comment = forms.CharField(widget=forms.Textarea,label=_("Message"))
    image = forms.FileField(widget=ResubmitFileWidget(attrs={'accept':'image/*'}),required=False)

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '')
        cleaned_comment = strip_tags(comment)

        if cleaned_comment == '':
            self._errors['comment'] = [_('This field is required.')]

            return ValueError

        return comment

    def clean_image(self):
        image = self.cleaned_data.get('image', False)

        if image:
            if hasattr(image, '_size'):
                if image._size > self.MAX_UPLOAD_SIZE:
                    self._errors['image'] = [_("The image is too large. It should have less than 5MB.")]

                    return ValueError

        return image

InlinePendenciesFormset = inlineformset_factory(Bulletin, Pendencies, form = PendenciesLimitedForm, extra = 1, max_num = 3, validate_max = True, can_delete = True)
