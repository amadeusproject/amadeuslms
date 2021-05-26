""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
# coding=utf-8
from django import forms
from datetime import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import os
import json
from django.conf import settings
from .base_plugin.classes import H5PDjango
from .base_plugin.module import h5pInsert, h5pGetContent
from .base_plugin.editor.editormodule import createContent

from file_resubmit.widgets import ResubmitFileWidget

from subjects.models import Tag
from subjects.forms import ParticipantsMultipleChoiceField

from .models import H5P

def handleUploadedFile(files, filename):
    tmpdir = os.path.join(settings.MEDIA_ROOT, 'h5pp', 'tmp')

    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    with open(os.path.join(tmpdir, filename), 'wb+') as destination:
        for chunk in files.chunks():
            destination.write(chunk)

    return {'folderPath': tmpdir, 'path': os.path.join(tmpdir, filename)}

class H5PForm(forms.ModelForm):
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024

    subject = None
    control_subject = forms.CharField(widget=forms.HiddenInput())
    students = ParticipantsMultipleChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")

        super(H5PForm, self).__init__(*args, **kwargs)


        self.subject = kwargs["initial"].get("subject", None)

        if self.instance.id:
            self.subject = self.instance.topic.subject
            self.initial["tags"] = ", ".join(
                self.instance.tags.all().values_list("name", flat=True)
            )

        self.initial["control_subject"] = self.subject.id

        self.fields["students"].queryset = self.subject.students.all()
        self.fields["groups"].queryset = self.subject.group_subject.all()

    tags = forms.CharField(label=_("Tags"), required=False)

    class Meta:
        model = H5P
        fields = [
            "name",
            "file",
            "data_ini",
            "data_end",
            "brief_description",
            "all_students",
            "students",
            "groups",
            "show_window",
            "visible",
        ]
        widgets = {
            "brief_description": forms.Textarea,
            "students": forms.SelectMultiple,
            "groups": forms.SelectMultiple,
            "file": ResubmitFileWidget(),
        }

    def clean(self):
        cleaned_data = super(H5PForm, self).clean()

        h5pfile = cleaned_data.get('file')
        
        if "file" in self.request.FILES:
            interface = H5PDjango(self.request.user)
            paths = handleUploadedFile(h5pfile, h5pfile.name)
            validator = interface.h5pGetInstance(
                'validator', paths['folderPath'], paths['path'])

            if not validator.isValidPackage(False, False):
                raise forms.ValidationError(_('The uploaded file was not a valid h5p package.'))

            _mutable = self.request.POST._mutable

            self.request.POST._mutable = True

            self.request.POST['file_uploaded'] = True
            self.request.POST['disable'] = 0
            self.request.POST['author'] = self.request.user.username
            self.request.POST['h5p_upload'] = paths['path']
            self.request.POST['h5p_upload_folder'] = paths['folderPath']

            self.request.POST._mutable = _mutable

            if not h5pInsert(self.request, interface):
                raise forms.ValidationError('Error during saving the content.')

        data_ini = cleaned_data.get("data_ini", None)
        data_end = cleaned_data.get("data_end", None)
        name = cleaned_data.get("name", "")

        topics = self.subject.topic_subject.all()

        for topic in topics:
            if self.instance.id:
                same_name = (
                    topic.resource_topic.filter(name__unaccent__iexact=name)
                    .exclude(id=self.instance.id)
                    .count()
                )
            else:
                same_name = topic.resource_topic.filter(
                    name__unaccent__iexact=name
                ).count()

            if same_name > 0:
                self.add_error(
                    "name", _("This subject already has a h5p resource with this name")
                )

                break

        if data_ini:
            if not data_ini == ValueError:
                if not self.instance.id and data_ini.date() < datetime.today().date():
                    self.add_error(
                        "data_ini",
                        _(
                            "This input should be filled with a date equal or after today's date."
                        ),
                    )

                if data_ini.date() < self.subject.init_date:
                    self.add_error(
                        "data_ini",
                        _(
                            'This input should be filled with a date equal or after the subject begin date.("%s")'
                        )
                        % (self.subject.init_date),
                    )

                if data_ini.date() > self.subject.end_date:
                    self.add_error(
                        "data_ini",
                        _(
                            'This input should be filled with a date equal or before the subject end date.("%s")'
                        )
                        % (self.subject.end_date),
                    )
        else:
            self.add_error("data_ini", _("This field is required"))

        if data_end:
            if not data_end == ValueError:
                if not self.instance.id and data_end.date() < datetime.today().date():
                    self.add_error(
                        "data_end",
                        _(
                            "This input should be filled with a date equal or after today's date."
                        ),
                    )

                if data_end.date() < self.subject.init_date:
                    self.add_error(
                        "data_end",
                        _(
                            'This input should be filled with a date equal or after the subject begin date.("%s")'
                        )
                        % (self.subject.init_date),
                    )

                if data_end.date() > self.subject.end_date:
                    self.add_error(
                        "data_end",
                        _(
                            'This input should be filled with a date equal or before the subject end date.("%s")'
                        )
                        % (self.subject.end_date),
                    )

                if not data_ini == ValueError and data_ini and data_end < data_ini:
                    self.add_error(
                        "data_end",
                        _(
                            "This input should be filled with a date equal or after the date stabilished for the init."
                        ),
                    )
        else:
            self.add_error("data_end", _("This field is required"))

        return cleaned_data

    def save(self, commit=True):
        super(H5PForm, self).save(commit=True)

        self.instance.save()

        previous_tags = self.instance.tags.all()

        tags = self.cleaned_data["tags"].split(",")

        # Excluding unwanted tags
        for prev in previous_tags:
            if not prev.name in tags:
                self.instance.tags.remove(prev)

        for tag in tags:
            tag = tag.strip()

            exist = Tag.objects.filter(name=tag).exists()

            if exist:
                new_tag = Tag.objects.get(name=tag)
            else:
                new_tag = Tag.objects.create(name=tag)

            if not new_tag in self.instance.tags.all():
                self.instance.tags.add(new_tag)

        return self.instance