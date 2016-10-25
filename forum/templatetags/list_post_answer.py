from django import template

from django.core.paginator import Paginator, EmptyPage
from django.http import Http404

from forum.models import PostAnswer

register = template.Library()

"""
 Template tag to load all the posts of a post
"""

@register.inclusion_tag('post_answers/post_answer_list.html')
def list_post_answer(request, post):
    context = {
        'request': request,
    }

    answers = PostAnswer.objects.filter(post = post)

    paginator = Paginator(answers, 5)

    try:
        page_number = int(request.GET.get('page_answer', 1))
    except ValueError:
        raise Http404

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        raise Http404

    context['paginator'] = paginator
    context['page_obj'] = page_obj

    context['answers'] = page_obj.object_list
    context['post'] = post

    return context