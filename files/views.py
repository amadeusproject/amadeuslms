from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rolepermissions.mixins import HasRoleMixin
from rolepermissions.verifications import has_role
from .forms import FileForm, UpdateFileForm
from .models import TopicFile
from .utils import mime_type_to_material_icons
from courses.models import Topic
from core.decorators import log_decorator
from core.models import Log, MimeType
from core.mixins import LogMixin, NotificationMixin
from django.urls import reverse
from datetime import datetime

# Create your views here.
class CreateFile(LoginRequiredMixin, HasRoleMixin, LogMixin, NotificationMixin, generic.edit.CreateView):
	log_component = 'file'
	log_resource = 'file'
	log_action = 'create'
	log_component = {}

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = TopicFile
	template_name = 'files/create_file.html'
	form_class = FileForm
	success_url = reverse_lazy('course:file:render_file')

	def form_invalid(self, form, **kwargs):
		context = super(CreateFile, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		self.object.topic = topic
		
		self.object.name = str(self.object)
		

		# Set MimeType
		file = self.request.FILES['file_url']
		try:
			if file:
				file_type = file.content_type

				# Check if exist a mimetype in database
				try:
					self.object.file_type = MimeType.objects.get(typ = file_type)
				# Create if not
				except:
					mtype = MimeType.objects.create(
						typ = file_type,
						icon = mime_type_to_material_icons[file_type]
					)
					mtype.save()
					self.object.file_type = mtype
		except:
			print('File not uploaded')
			# self.object.file_type = MimeType.objects.get(id = 1)

		self.object.save()
		#CREATE NOTIFICATION
		super(CreateFile, self).createNotification(message="uploaded a File "+ self.object.name, actor=self.request.user,
			resource_name=self.object.name, resource_link= reverse('course:view_topic', args=[self.object.topic.slug]), 
			users=self.object.topic.subject.students.all())

		self.log_context['file_id'] = self.object.id
		self.log_context['file_name'] = self.object.name
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['course_id'] = self.object.topic.subject.course.id
		self.log_context['course_name'] = self.object.topic.subject.course.name
		self.log_context['course_slug'] = self.object.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

		super(CreateFile, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return self.get_success_url()

	def get_context_data(self, **kwargs):
		context = super(CreateFile, self).get_context_data(**kwargs)
		topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
		context["topic"] = topic
		context['subject'] = topic.subject
		context['subjects'] = topic.subject.course.subjects.all()
		try:
			context['latest_file'] = TopicFile.objects.latest('id')
		except:
			pass
		return context

	def get_success_url(self):
		self.success_url = redirect('course:file:render_file', id = self.object.id)
		
		return self.success_url

@log_decorator("file", "viewed", "file")
def render_file(request, id):
	template_name = 'files/render_file.html'
	file = get_object_or_404(TopicFile, id = id)

	context = {
		'file': file
	}

	log_context = {}
	log_context['file_id'] = file.id
	log_context['file_name'] = file.name
	log_context['topic_id'] = file.topic.id
	log_context['topic_name'] = file.topic.name
	log_context['topic_slug'] = file.topic.slug
	log_context['subject_id'] = file.topic.subject.id
	log_context['subject_name'] = file.topic.subject.name
	log_context['subject_slug'] = file.topic.subject.slug
	log_context['course_id'] = file.topic.subject.course.id
	log_context['course_name'] = file.topic.subject.course.name
	log_context['course_slug'] = file.topic.subject.course.slug
	log_context['course_category_id'] = file.topic.subject.course.category.id
	log_context['course_category_name'] = file.topic.subject.course.category.name

	request.log_context = log_context

	return render(request, template_name, context)


class UpdateFile(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.UpdateView):
	log_component = 'file'
	log_resource = 'file'
	log_action = 'update'
	log_context = {}

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = TopicFile
	template_name = 'files/update_file.html'
	form_class = UpdateFileForm
	context_object_name = 'file'
	success_url = reverse_lazy('course:file:render_file')

	def form_invalid(self, form, **kwargs):
		context = super(UpdateFile, self).form_invalid(form)
		context.status_code = 400

		return context

	
	def form_valid(self, form):
		self.object = form.save()

		self.log_context['file_id'] = self.object.id
		self.log_context['file_name'] = self.object.name
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['course_id'] = self.object.topic.subject.course.id
		self.log_context['course_name'] = self.object.topic.subject.course.name
		self.log_context['course_slug'] = self.object.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

		super(UpdateFile, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return super(UpdateFile, self).form_valid(form)

	def get_object(self, queryset=None):
	    return get_object_or_404(TopicFile, slug = self.kwargs.get('slug'))

	def get_success_url(self):
		self.success_url = reverse_lazy('course:file:render_file', args = (self.object.id, ))
		
		return self.success_url


class DeleteFile(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.DeleteView):
	log_component = 'file'
	log_resource = 'file'
	log_action = 'delete'
	log_context = {}

	allowed_roles = ['professor', 'system_admin']
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	model = TopicFile
	template_name = 'files/delete_file.html'

	def dispatch(self, *args, **kwargs):
		file = get_object_or_404(TopicFile, slug = self.kwargs.get('slug'))
		if(not (file.topic.owner == self.request.user) and not(has_role(self.request.user, 'system_admin')) ):
			return self.handle_no_permission()
		return super(DeleteFile, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(DeleteFile, self).get_context_data(**kwargs)
		context['course'] = self.object.topic.subject.course
		context['subject'] = self.object.topic.subject
		context['file'] = self.object
		context["topic"] = self.object.topic
		return context

	def get_success_url(self):
		self.log_context['file_id'] = self.object.id
		self.log_context['file_name'] = self.object.name
		self.log_context['topic_id'] = self.object.topic.id
		self.log_context['topic_name'] = self.object.topic.name
		self.log_context['topic_slug'] = self.object.topic.slug
		self.log_context['subject_id'] = self.object.topic.subject.id
		self.log_context['subject_name'] = self.object.topic.subject.name
		self.log_context['subject_slug'] = self.object.topic.subject.slug
		self.log_context['course_id'] = self.object.topic.subject.course.id
		self.log_context['course_name'] = self.object.topic.subject.course.name
		self.log_context['course_slug'] = self.object.topic.subject.course.slug
		self.log_context['course_category_id'] = self.object.topic.subject.course.category.id
		self.log_context['course_category_name'] = self.object.topic.subject.course.category.name

		super(DeleteFile, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('course:view_topic', kwargs={'slug' : self.object.topic.slug})