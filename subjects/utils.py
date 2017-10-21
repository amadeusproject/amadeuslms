""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


#    File used to store useful subject functions    #
from categories.models import Category
from .models import Subject
from django.db.models import Q

def has_student_profile(user, category):
	for subject in category.subject_category.all():
		if subject.students.filter(id = user.id).exists() and subject.visible:
			return True

	return False

def has_professor_profile(user, category):
	for subject in category.subject_category.all():
		if subject.professor.filter(id = user.id).exists() and subject.visible:
			return True

	return False

def get_category_page(categories, slug, per_page):
	total = 1

	for category in categories:
		if category.slug == slug:
			return total / per_page + 1

		total += 1

	return 1

def count_subjects( user, all_subs = True):
	total = 0
	pk = user.pk

	"""for category in categories:
		if not all_subs:
			for subject in category.subject_category.all():
				if user in subject.students.all() or user in subject.professor.all() or user in subject.category.coordinators.all():
					total += 1
		else:		
			total += category.subject_category.count()"""
	if all_subs:
		#total += Category.objects.filter(Q(coordinators__pk = pk) | Q(visible=True) ).distinct().count()
		total = Subject.objects.filter(Q(students__pk=pk) | Q(professor__pk=pk) | Q(category__coordinators__pk=pk) | Q(visible = True)).distinct().count()
	else:
		
		total = Subject.objects.filter(Q(students__pk=pk) | Q(professor__pk=pk) | Q(category__coordinators__pk=pk)).distinct().count()
	return total