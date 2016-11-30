from django import template
from exercise.models import Exercise

register = template.Library()


@register.inclusion_tag('exercise/exercise_list.html')
def list_topic_exercise(request, topic):
    context = {
        'request': request,
    }
    context['exercises'] = Exercise.objects.filter(topic=topic)

    return context


@register.inclusion_tag('exercise/exercise_edit.html')
def list_topic_exercise_edit(request, topic):
    context = {
        'request': request,
    }
    context['exercises'] = Exercise.objects.filter(topic=topic)
    context['topic'] = topic

    return context
