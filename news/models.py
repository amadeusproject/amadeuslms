""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models

# Create your models here.
from autoslug.fields import AutoSlugField

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from users.models import User

valid_formats = ['image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png']

def validate_img_extension(value):
	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('File not supported.'))

class News(models.Model):
	title = models.CharField( _("Title"), unique = True,max_length= 200)
	slug = AutoSlugField(_("Slug"),populate_from='title',unique=True)
	image = models.ImageField(verbose_name = _('News Image'), upload_to = 'news/', validators = [validate_img_extension],blank= True)
	content = models.TextField(_('News Content'), blank = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	creator = models.ForeignKey(User, verbose_name = _('Creator'), related_name = "news_creator_user", null = True)
	
	class Meta:
		verbose_name = _('News')
		verbose_name_plural = _('News')

	def __str__(self):
		return self.title
