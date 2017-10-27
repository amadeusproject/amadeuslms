""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
import os
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy

from topics.models import Resource
# Create your models here.
valid_formats = [
    'application/pdf'
]

def validate_file_extension(value):
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
        return reverse_lazy('pdf_files:view', args = (), kwargs = {'slug': self.slug})

    def update_link(self):
        return 'pdf_files:update'

    def delete_link(self):
        return 'pdf_files:delete'

    def delete_message(self):
        return _('Are you sure you want delete the PDF File')
