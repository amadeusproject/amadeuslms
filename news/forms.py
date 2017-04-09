from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import News
from resubmit.widgets import ResubmitFileWidget


class NewsForm(forms.ModelForm):
    MAX_UPLOAD_SIZE = 5*1024*1024
    class Meta:
        model = News
        fields = ['title','image','content']
        widgets = {
            'content': forms.Textarea,
            'image': ResubmitFileWidget(attrs={'accept':'image/*'}),

        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if title == '':
            self._errors['name'] = [_('This field is required')]

            return ValueError

        return title
    def clean_image(self):
        image = self.cleaned_data.get('image', False)

        if image:
            if hasattr(image, '_size'):
                if image._size > self.MAX_UPLOAD_SIZE:
                    self._errors['image'] = [_("The image is too large. It should have less than 5MB.")]
                    return ValueError
        else:
            self._errors['image'] = [_("This field is required.")]

            return ValueError

            return image
