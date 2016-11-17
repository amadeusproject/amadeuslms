from .forms import ExerciseForm, UpdateExerciseForm
from .models import Exercise
from core.decorators import log_decorator
from core.mixins import LogMixin, NotificationMixin
from core.models import Log, MimeType
from courses.models import Topic
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from files.utils import mime_type_to_material_icons
from rolepermissions.mixins import HasRoleMixin
from rolepermissions.verifications import has_role
from users.models import User


class CreateExercise(LoginRequiredMixin, HasRoleMixin, LogMixin, NotificationMixin, generic.CreateView):
    log_component = 'exercise'
    log_resource = 'exercise'
    log_action = 'create'
    log_component = {}

    allowed_roles = ['professor', 'student']
    login_url = reverse_lazy("core:home")
    redirect_field_name = 'next'
    model = Exercise
    template_name = 'exercise/create_exercise.html'
    form_class = ExerciseForm
    success_url = reverse_lazy('course:exercise:render_exercise')

    log_component = "subject"
    log_resource = "exercise"
    log_action = "create"
    log_context = {}

    def form_invalid(self, form, **kwargs):
        context = super(CreateExercise, self).form_invalid(form)
        context.status_code = 400

        return context

    def form_valid(self, form):
        self.object = form.save(commit = False)
        topic = get_object_or_404(Topic, slug = self.kwargs.get('slug'))
        self.object.topic = topic
        self.object.name = str(self.object)
        self.object.professors = topic.subject.professors
        self.object.students = topic.subject.students

        # Set MimeType
        exercise = self.request.FILES['exercise_url']
        self.object.file_exercise.file = exercise
        try:
            if exercise:
                exercise_type = exercise.content_type

                # Check if exist a mimetype in database
                try:
                    self.object.file_exercise.file_type = MimeType.objects.get(typ = exercise_type)
                # Create if not
                except:
                    mtype = MimeType.objects.create(
                        typ = exercise_type,
                        icon = mime_type_to_material_icons[exercise_type]
                    )
                    mtype.save()
                    self.object.file_exercise.file_type = mtype
        except:
            print('Exercise not uploaded')

        self.object.save()
        #CREATE LOG 
        self.log_context['topic_id'] = topic.id
        self.log_context['topic_name'] = topic.name
        self.log_context['topic_slug'] = topic.slug
        self.log_context['subject_id'] = topic.subject.id
        self.log_context['subject_name'] = topic.subject.name
        self.log_context['subject_slug'] = topic.subject.slug

        super(CreateExercise, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)



        #CREATE NOTIFICATION
        super(CreateExercise, self).createNotification(message="uploaded a Exercise "+ self.object.name, actor=self.request.user,
            resource_name=self.object.name, resource_link= reverse('course:view_topic', args=[self.object.topic.slug]), 
            users=self.object.topic.subject.students.all())

        self.log_context['exercise_id'] = self.object.id
        self.log_context['exercise_name'] = self.object.name
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

        super(CreateExercise, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super(CreateExercise, self).get_context_data(**kwargs)
        topic = get_object_or_404(Topic, slug=self.kwargs.get('slug'))
        context['topic'] = topic
        context['subject'] = topic.subject
        context['subjects'] = topic.subject.course.subjects.all()
        context['form'] = self.form_class

        try:
            context['latest_exercise'] = Exercise.objects.latest('id')
        except:
            pass
        return context

    def get_success_url(self):
        self.success_url = redirect('course:exercise:render_exercise', id = self.object.id)
        
        return self.success_url


def render_exercise(request, id):
    template_name = 'exercise/render_exercise.html'
    exercise = get_object_or_404(Exercise, id = id)

    context = {
        'exercise': exercise
    }

    log_context = {}
    log_context['exercise_id'] = exercise.id
    log_context['exercise_name'] = exercise.name
    log_context['topic_id'] = exercise.topic.id
    log_context['topic_name'] = exercise.topic.name
    log_context['topic_slug'] = exercise.topic.slug
    log_context['subject_id'] = exercise.topic.subject.id
    log_context['subject_name'] = exercise.topic.subject.name
    log_context['subject_slug'] = exercise.topic.subject.slug
    log_context['course_id'] = exercise.topic.subject.course.id
    log_context['course_name'] = exercise.topic.subject.course.name
    log_context['course_slug'] = exercise.topic.subject.course.slug
    log_context['course_category_id'] = exercise.topic.subject.course.category.id
    log_context['course_category_name'] = exercise.topic.subject.course.category.name

    request.log_context = log_context

    return render(request, template_name, context)


class UpdateExercise(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.UpdateView):
    log_component = 'exercise'
    log_resource = 'exercise'
    log_action = 'update'
    log_context = {}

    allowed_roles = ['student']
    login_url = reverse_lazy("core:home")
    redirect_field_name = 'next'
    model = Exercise
    template_name = 'exercise/update_exercise.html'
    form_class = UpdateExerciseForm
    context_object_name = 'exercise'
    success_url = reverse_lazy('course:exercise:render_exercise')

    def form_invalid(self, form, **kwargs):
        context = super(UpdateExercise, self).form_invalid(form)
        context.status_code = 400

        return context

    
    def form_valid(self, form):
        self.object = form.save()

        self.log_context['exercise_id'] = self.object.id
        self.log_context['exercise_name'] = self.object.name
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

        super(UpdateExercise, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return super(UpdateExercise, self).form_valid(form)

    def get_object(self, queryset=None):
        return get_object_or_404(Exercise, slug = self.kwargs.get('slug'))

    def get_success_url(self):
        self.success_url = reverse_lazy('course:exercise:render_exercise', args = (self.object.id, ))
        
        return self.success_url


class DeleteExercise(LoginRequiredMixin, HasRoleMixin, LogMixin, generic.DeleteView):
    log_component = 'exercise'
    log_resource = 'exercise'
    log_action = 'delete'
    log_context = {}

    allowed_roles = ['student']
    login_url = reverse_lazy("core:home")
    redirect_field_name = 'next'
    model = Exercise
    template_name = 'exercise/delete_exercise.html'

    def dispatch(self, *args, **kwargs):
        exercise = get_object_or_404(Exercise, slug = self.kwargs.get('slug'))
        if(not (exercise.topic.owner == self.request.user) and not(has_role(self.request.user, 'system_admin')) ):
            return self.handle_no_permission()
        return super(DeleteExercise, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteExercise, self).get_context_data(**kwargs)
        context['course'] = self.object.topic.subject.course
        context['subject'] = self.object.topic.subject
        context['exercise'] = self.object
        context["topic"] = self.object.topic
        return context

    def get_success_url(self):
        self.log_context['exercise_id'] = self.object.id
        self.log_context['exercise_name'] = self.object.name
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

        super(DeleteExercise, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

        return reverse_lazy('course:view_topic', kwargs={'slug' : self.object.topic.slug})