""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import os
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy

from topics.models import Resource

valid_formats = [
	'image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png',
	'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
	'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
	'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
	'application/vnd.openxmlformats-officedocument.presentationml.presentation',
	'application/vnd.ms-excel','text/html','application/msword','application/vnd.oasis.opendocument.presentation',
	'application/vnd.oasis.opendocument.spreadsheet','application/vnd.oasis.opendocument.text',
	'application/pdf',
	'application/vnd.ms-powerpoint'
]

def validate_file_extension(value):
	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('Please select a valid file. The uploaded file must have one of the following extensions: .doc, .docx, .html, .jpg, .odp, .ods, .odt, .pdf, .png, .ppt, .pptx, .xlx e .xlsx'))

class FileLink(Resource):
	file_content = models.FileField(_('File'), blank = True, upload_to = 'files/', validators = [validate_file_extension])

	class Meta:
		verbose_name = _('File Link')
		verbose_name_plural = _('File Links')

	@property
	def filename(self):
		return os.path.basename(self.file_content.name)

	def __str__(self):
		return self.name

	def access_link(self):
		return reverse_lazy('file_links:download', args = (), kwargs = {'slug': self.slug})

	def update_link(self):
		return 'file_links:update'

	def delete_link(self):
		return 'file_links:delete'

	def delete_message(self):
		return _('Are you sure you want delete the file link')
