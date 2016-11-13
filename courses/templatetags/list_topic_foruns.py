from django import template

from links.models import Link
from forum.models import Forum
from poll.models import Poll
from exam.models import Exam
from files.models import TopicFile
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


@register.inclusion_tag('subject/poll_item_actions.html')
def list_topic_poll(request, topic):
    context = {
        'request': request,
    }

    context['polls'] = Poll.objects.filter(topic = topic)
    context['topic'] = topic

    return context


@register.inclusion_tag('subject/poll_item_actions_teacher.html')
def list_topic_poll_teacher(request, topic):
    context = {
        'request': request,
    }

    context['polls'] = Poll.objects.filter(topic = topic)
    context['topic'] = topic

    return context


@register.inclusion_tag('topic/list_file.html')
def list_topic_file(request, topic):
    context = {
        'request': request,
    }

    context['files'] = TopicFile.objects.filter(topic = topic)
    context['topic'] = topic

    return context


@register.inclusion_tag('topic/list_file_edit.html')
def list_topic_file_edit(request, topic):
    context = {
        'request': request,
    }

    context['files'] = TopicFile.objects.filter(topic = topic)
    context['topic'] = topic

    return context


@register.inclusion_tag('topic/link_topic_list_edit.html')
def list_topic_link_edit(request,topic):
    context = {
        'request':request
    }
    context['links'] = Link.objects.filter(topic = topic)
    context['topic'] = topic
    return context


@register.inclusion_tag('topic/link_topic_list.html')
def list_topic_link(request,topic):
    context = {
        'request':request
    }
    context['links'] = Link.objects.filter(topic = topic)
    context['topic'] = topic
    return context
