from django import template
from .models import Exercise

register = template.Library()


@register.inclusion_tag('subject/form_view_student.html')
def list_topic_exercise(request, exercise):
    context = {
        'request': request,
    }

    context['exercises'] = Exercise.objects.filter(exercise = exercise)

    return context


@register.inclusion_tag('topic/list_file_edit.html')
def list_topic_exercise_edit(request, exercise):
    context = {
        'request': request,
    }

    context['exercises'] = Exercise.objects.filter(exercise = exercise)
    context['exercise'] = exercise

    return context
