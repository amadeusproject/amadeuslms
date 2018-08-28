""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from rest_framework import serializers
from django.shortcuts import get_object_or_404

from subjects.models import Subject

from .models import Topic

class TopicSerializer(serializers.ModelSerializer):
	def validate(self, data):
		subject = self.context.get('subject', None)

		if subject:
			subject = get_object_or_404(Subject, slug = subject)
			topic = Topic.objects.filter(subject = subject, name__unaccent__iexact = data["name"])
			
			if topic.exists():
				data = topic[0].__dict__
			else:
				data["id"] = ""
				data["subject"] = subject
				data["order"] = Topic.objects.filter(subject = subject).count() + 1

				if data["repository"] == True:
					topic = Topic.objects.filter(subject = subject, repository = True)

					if topic.exists():
						data = topic[0].__dict__
				
		return data

	class Meta:
		model = Topic
		exclude = ('subject',)

