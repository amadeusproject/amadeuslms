""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.utils import timezone
from django import forms
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.forms.models import inlineformset_factory

from file_resubmit.widgets import ResubmitFileWidget

from subjects.models import Tag
from subjects.forms import ParticipantsMultipleChoiceField

from .models import MaterialDelivery, SupportMaterial, StudentMaterial, TeacherEvaluation, valid_formats

class MaterialDeliveryForm(forms.ModelForm):
    subject = None
    topic = None

    students = ParticipantsMultipleChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        super(MaterialDeliveryForm, self).__init__(*args, **kwargs)
        self.subject = kwargs.get("initial").get("subject", None)
        self.topic = kwargs["initial"].get("topic", None)

        if self.instance.id:
            self.subject = self.instance.topic.subject
            self.topic = self.instance.topic
            self.initial["tags"] = ", ".join(
                self.instance.tags.all().values_list("name", flat=True)
            )

        self.fields["students"].queryset = self.subject.students.all()
        self.fields["groups"].queryset = self.subject.group_subject.all()

    tags = forms.CharField(label = _("Tags"), required = False)

    class Meta:
        model = MaterialDelivery
        fields = [
            "name",
            "presentation",
            "data_ini",
            "data_end",
            "brief_description",
            "show_window",
            "all_students",
            "students",
            "groups",
            "visible",
        ]
        labels = {
            "name": _("Material Delivery Name"),
        }
        widgets = {
            "presentation": forms.Textarea,
            "brief_description": forms.Textarea,
            "students": forms.SelectMultiple,
            "groups": forms.SelectMultiple,
        }

    def clean(self):
        cleaned_data = super(MaterialDeliveryForm, self).clean()

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
                    "name", _("This subject already has a material delivery with this name")
                )

                break

        todaysDate = timezone.localtime(timezone.now()).date()

        if data_ini:
            if not data_ini == ValueError:
                if not self.instance.id and data_ini.date() < todaysDate:
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
                if not self.instance.id and data_end.date() < todaysDate:
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

    def save(self, commit = True):
        super(MaterialDeliveryForm, self).save(commit=True)

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

class SupportMaterialForm(forms.ModelForm):
    MAX_UPLOAD_SIZE = 30 * 1024 * 1024

    class Meta:
        model = SupportMaterial
        fields = ["file"]
        widgets = {
            "file": ResubmitFileWidget(
                attrs={
                    "accept": ", ".join(valid_formats)
                }
            ),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file", False)

        if file:
            if hasattr(file, "_size"):
                if file._size > self.MAX_UPLOAD_SIZE:
                    self._errors["file"] = [
                        _("The file is too large. It should have less than 30MB.")
                    ]

                    return ValueError

        return file

class StudentMaterialForm(forms.ModelForm):
    MAX_UPLOAD_SIZE = 30 * 1024 * 1024

    class Meta:
        model = StudentMaterial
        fields = ["commentary", "file"]
        labels = {
            "commentary": _("Material Description"),
        }
        widgets = {
            "commentary": forms.Textarea,
            "file": ResubmitFileWidget(
                attrs={
                    "accept": ", ".join(valid_formats)
                }
            ),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file", False)

        if file:
            if hasattr(file, "_size"):
                if file._size > self.MAX_UPLOAD_SIZE:
                    self._errors["file"] = [
                        _("The file is too large. It should have less than 30MB.")
                    ]

                    return ValueError

        elif not self.instance.pk:
            self._errors["file"] = [_("This field is required.")]

            return ValueError

        return file

class TeacherEvaluationForm(forms.ModelForm):
    MAX_UPLOAD_SIZE = 30 * 1024 * 1024

    evaluation = forms.ChoiceField(choices=[(a, a) for a in range(100, -1, -1)])

    class Meta:
        model = TeacherEvaluation
        fields = ["evaluation", "commentary", "file"]
        widgets = {
            "evaluation": forms.Select,
            "commentary": forms.Textarea,
            "file": ResubmitFileWidget(
                attrs={
                    "accept": ", ".join(valid_formats)
                }
            ),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file", False)

        if file:
            if hasattr(file, "_size"):
                if file._size > self.MAX_UPLOAD_SIZE:
                    self._errors["file"] = [
                        _("The file is too large. It should have less than 30MB.")
                    ]

                    return ValueError

        elif not self.instance.pk:
            self._errors["file"] = [_("This field is required.")]

            return ValueError

        return file

InlineSupportMaterialFormset = inlineformset_factory(
    MaterialDelivery,
    SupportMaterial,
    form=SupportMaterialForm,
    min_num=1,
    extra=0,
    can_delete=True
)