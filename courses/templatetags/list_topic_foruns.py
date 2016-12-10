from django import template

from links.models import Link
from forum.models import Forum
from poll.models import Poll
from files.models import TopicFile
from django.db.models import Q
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
    all_polls = Poll.objects.filter(topic = topic)
    my_polls = []
    for poll in all_polls.all():
        if ((request.user in poll.students.all())
            or request.user in poll.topic.subject.professors.all()):
            my_polls.append(poll)
    context['polls'] = my_polls
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
