from django import template
from courses.models import Exercise

register = template.Library()


@register.inclusion_tag('exercise/exercise_list.html')
def list_topic_exercise(request):
    context = {
        'request': request,
    }
    context['exercises'] = Exercise.objects.all()

    return context


@register.inclusion_tag('exercise/exercise_edit.html')
def list_topic_exercise_edit(request, exercise):
    context = {
        'request': request,
    }
    context['exercises'] = Exercise.objects.all()
    context['exercise'] = exercise

    return context
