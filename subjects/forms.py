from django import forms
from django.utils.translation import ugettext_lazy as _
import datetime
from .models import Subject, Tag

class CreateSubjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateSubjectForm, self).__init__(*args, **kwargs)
        
        if not kwargs['instance'] is None:
            self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))

    # TODO: Define form fields here
    tags = forms.CharField(label = _('Tags'), required = False)

    class Meta:
        model = Subject

        fields = ('name', 'description_brief', 'description', 'init_date', 'end_date','subscribe_begin', 'subscribe_end',
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

        #self.instance.save()

        return self.instance

    def clean(self):
        cleaned_data = super(CreateSubjectForm, self).clean()
        print("este")
        if cleaned_data['subscribe_begin'] > cleaned_data['end_date']:
            raise forms.ValidationError(_('Subscribe period should be  between course time'))
        return cleaned_data
    def clean_subscribe_begin(self):
        subscribe_begin = self.cleaned_data['subscribe_begin']
        #if subscribe_begin < datetime.datetime.today().date():
            #self._errors['subscribe_begin'] = _('this date must be today or after')
            #raise forms.ValidationError(_(''))
        return subscribe_begin

class CreateTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name',)
    