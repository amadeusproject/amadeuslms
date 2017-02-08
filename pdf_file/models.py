from django.db import models
from django.utils.translation import ugettext_lazy as _
import os
from django.core.exceptions import ValidationError

from topics.models import Resource
# Create your models here.
def validate_file_extension(value):
    valid_formats = [
        'application/pdf'
    ]
    
    if hasattr(value.file, 'content_type'):
        if not value.file.content_type in valid_formats:
            raise ValidationError(_('File not supported, use PDF format instead.'))

class PDFFile(Resource):
    file = models.FileField(_('File'), upload_to='files/', validators = [validate_file_extension])
    class Meta:
        verbose_name = "PDFFile"
        verbose_name_plural = "PDFFiles"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.name

    def access_link(self):
        return 'pdf_files:view'

    def update_link(self):
        return 'pdf_files:update'

    def delete_link(self):
        return 'pdf_files:delete'

    def delete_message(self):
        return _('Are you sure you want delete the PDF File')
