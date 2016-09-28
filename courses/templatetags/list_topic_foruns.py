from django import template

from forum.models import Forum

register = template.Library()

"""
 Template tag to load all the foruns of a post
"""

@register.inclusion_tag('topic/list_topic_foruns.html')
def list_topic_foruns(request, topic):
    context = {
        'request': request,
    }

    context['foruns'] = Forum.objects.filter(topic = topic)

    return context