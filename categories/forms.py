""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django import forms
from .models import Category

from django.utils.translation import ugettext_lazy as _

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ( 'name', 'description', 'visible', 'coordinators', )
        widgets = {
            'description': forms.Textarea,
            'coordinators' : forms.SelectMultiple,
        }
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.instance.id:
            same_name = Category.objects.filter(name__unaccent__iexact = name).exclude(id = self.instance.id)
        else:
            same_name = Category.objects.filter(name__unaccent__iexact = name)

        if same_name.count() > 0:
            self._errors['name'] = [_('There is another category with this name, try another one.')]

        return name
