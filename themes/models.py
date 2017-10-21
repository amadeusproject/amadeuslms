""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from os import path
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.staticfiles.templatetags.staticfiles import static

def validate_img_extension(value):
	valid_formats = ['image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png']

	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('File not supported.'))

class Themes(models.Model):
	title = models.CharField(_("Title"), max_length = 200, default = "Projeto Amadeus")
	favicon = models.ImageField(verbose_name = _("Favicon"), blank = True, null = True, upload_to = 'themes/', validators = [validate_img_extension])
	small_logo = models.ImageField(verbose_name = _("Small Logo"), blank = True, null = True, upload_to = 'themes/', validators = [validate_img_extension])
	large_logo = models.ImageField(verbose_name = _("Large Logo"), blank = True, null = True, upload_to = 'themes/', validators = [validate_img_extension])
	high_contrast_logo = models.ImageField(verbose_name = _("High Contrast Logo"), blank = True, null = True, upload_to = 'themes/', validators = [validate_img_extension])
	footer_note = models.TextField(_("Footer Note"), blank = True)
	css_style = models.CharField(_("Css Style"), max_length = 50, default = "green", choices = (("green", _('Green')),("contrast",_('Contrast')),("red", _('Red')), ("black", _('Black'))))

	class Meta:
		verbose_name = _("Theme")
		verbose_name_plural = _("Themes")

	def __str__(self):
		return self.title

	@property
	def favicon_url(self):
		if self.favicon and hasattr(self.favicon, 'url'):
			if path.exists(self.favicon.path):
				return self.favicon.url

		return static('img/favicon_amadeus.png')

	@property
	def small_logo_url(self):
		if self.small_logo and hasattr(self.small_logo, 'url'):
			if path.exists(self.small_logo.path):
				return self.small_logo.url

		return static('img/logo_pequena_amadeus.png')

	@property
	def large_logo_url(self):
		if self.large_logo and hasattr(self.large_logo, 'url'):
			if path.exists(self.large_logo.path):
				return self.large_logo.url

		return static('img/logo_grande_amadeus.png')

	@property
	def high_contrast_logo_url(self):
		if self.high_contrast_logo and hasattr(self.high_contrast_logo, 'url'):
			if path.exists(self.high_contrast_logo.path):
				return self.high_contrast_logo.url

		return static('img/alto_contraste_logo_amadeus.png')
