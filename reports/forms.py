""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
import datetime

from django.forms.formsets import BaseFormSet


class BaseResourceAndTagFormset(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two links have the same anchor or URL
        and that all links have both an anchor and URL.
        """
        print(self.errors)
        if any(self.errors):
            return

        for form in self.forms:
        	pass

class ResourceAndTagForm(forms.Form):

	resource = forms.ChoiceField(label=_("Kind Of Resource"), required=True)
	tag  = forms.ChoiceField(label=_('Tag'))

	def __init__(self, *args, **kwargs):
		super(ResourceAndTagForm, self).__init__(*args, **kwargs)
		if kwargs.get('initial'):
			initial = kwargs['initial']
			self.fields['resource'].choices = [(classes.__name__.lower(), classes.__name__.lower()) for classes in initial['class_name']]
			self.fields['tag'].choices = [(tag.id, tag.name) for tag in initial['tag']]
		

class CreateInteractionReportForm(forms.Form):
	topic = forms.ChoiceField( label= _("Topics"), required=True)
	init_date = forms.DateField(required=True, label= _("Initial Date"))
	end_date = forms.DateField(required=True, label= _("Final Date"))

	from_mural = forms.BooleanField(required=False, label=_("From Mural"))
	from_messages = forms.BooleanField(required=False, label=_("Messages"))

	class Meta:
		fields = ('topic', 'init_date', 'end_date', 'from_mural' , 'from_messages')

	def __init__(self, *args, **kwargs):
		super(CreateInteractionReportForm, self).__init__(*args, **kwargs)
		initial = kwargs['initial']
		topics = list(initial['topic'])
		self.subject = initial['subject'] #so we can check date cleaned data
		self.fields['topic'].choices = [(topic.id, topic.name) for topic in topics]
		self.fields['topic'].choices.append((_("All"), _("All")))


	def clean(self):
		cleaned_data = super(CreateInteractionReportForm, self).clean()
		init_date = cleaned_data.get("init_date")
		end_date = cleaned_data.get("end_date")
		if init_date and end_date:
			if init_date > end_date:
				raise forms.ValidationError(_("The initial date can't be after the end one."))

	def clean_init_date(self):
		init_date = self.cleaned_data['init_date']
		if init_date < self.subject.init_date:
			self._errors['init_date'] = [_('This date should be right or after %s, which is when the subject started. ') % str(self.subject.init_date)]
		return init_date

	def clean_end_date(self):
		end_date = self.cleaned_data['end_date']
		if end_date > self.subject.end_date:
			self._errors['end_date'] = [_('This date should be right or before %s, which is when the subject finishes. ') % str(self.subject.end_date)]
		return end_date