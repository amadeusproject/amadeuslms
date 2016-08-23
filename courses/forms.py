from django import forms
from .models import Category, Course, Module

class CategoryForm(forms.ModelForm):

	class Meta:
		model = Category
		fields = ('name',)
		labels = {
			'name': 'Nome'
		}
		help_texts = {
			'name': 'Nome da categoria'
		}


class CourseForm(forms.ModelForm):

	class Meta:
		model = Course
		fields = ('name', 'objectivies', 'content', 'max_students', 'init_register_date', 'end_register_date',
					'init_date', 'end_date', 'image', 'category',)
		labels = {
			'name': 'Nome',
			'objectivies': 'Objetivos',
			'content': 'Programa',
			'max_students': 'Número máximo de alunos',
			'init_register_date': 'Data de início da inscrição do curso',
			'end_register_date': 'Data de término da inscrição do curso',
			'init_date': 'Data de início do curso',
			'end_date': 'Data de término do curso',
			'image': 'Imagem',
			'category': 'Categoria',
		}
		help_texts = {
			'name': 'Nome do curso',
			'objectivies': 'Objetivo do curso',
			'content': 'Módulos presentes no curso',
			'max_students': 'Número máximo de alunos que uma turma do curso pode ter',
			'init_register_date': 'Data em que começam as inscrições para o curso (dd/mm/yyyy)',
			'end_register_date': 'Data em que terminam as inscrições para o curso (dd/mm/yyyy)',
			'init_date': 'Data em que começa o curso (dd/mm/yyyy)',
			'end_date': 'Data em que termina o curso (dd/mm/yyyy)',
			'image': 'Imagem representativa do curso',
			'category': 'Categoria em que o curso se enquadra',
		}

class ModuleForm(forms.ModelForm):

	class Meta:
		model = Module
		fields = ('name', 'description', 'visible',)
		labels = {
			'name': 'Nome',
			'description': 'Descrição',
			'visible': 'Está visível?',
		}
		help_texts = {
			'name': 'Nome do módulo',
			'description': 'Descrição do módulo',
			'visible': 'O módulo está visível?',	
		}