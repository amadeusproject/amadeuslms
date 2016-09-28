from django import template

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

    context['answers'] = PostAnswer.objects.filter(post = post)

    return context