""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

# File used to store functions to handle permissions

from categories.models import Category
from subjects.models import Subject
from topics.models import Resource

"""
	Function to know if a user has permission to:
		- Edit Category
		- Delete Category
		- Create Subject
		- Replicate Subject
"""
def has_category_permissions(user, category):
	if user.is_staff:
		return True

	if category and category.coordinators.filter(id = user.id).exists():
		return True

	return False

"""
	Function to know if a user has permission to:
		- Edit Subject
		- Delete Subject
		- Create Topic inside Subject 
"""
def has_subject_permissions(user, subject):
	if user and user.is_staff:
		return True

	if subject.professor and subject.professor.filter(id = user.id).exists():
		return True

	if subject.category and subject.category.coordinators.filter(id = user.id).exists():
		return True

	return False

"""
	Function to know if user has permission to:
		- See subject
"""
def has_subject_view_permissions(user, subject):
	if has_subject_permissions(user, subject):
		return True

	if subject and subject.students.filter(id = user.id).exists():
		return True

	return False

"""
	Function to know if user is student of some subject in category
"""
def has_category_permission(user, cat_slug):
	exist = Subject.objects.filter(students__id = user.id, category__slug = cat_slug).exists()

	return exist

"""
	Function to know if user has permission to:
		- Access Resource
"""
def has_resource_permissions(user, resource):
	if has_subject_permissions(user, resource.topic.subject):
		return True

	if resource.visible or resource.topic.repository:
		if resource.all_students:
			if resource.topic.subject.students.filter(id = user.id).exists():
				return True

		if resource.students.filter(id = user.id).exists():
			return True

		if Resource.objects.filter(id = resource.id, groups__participants__pk = user.pk).exists():
			return True

	return False




