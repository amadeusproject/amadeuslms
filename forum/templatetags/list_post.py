from django import template

from forum.models import Post

register = template.Library()

"""
 Template tag to load all the posts of a post
"""

@register.inclusion_tag('post/post_list.html')
def list_posts(request, forum):
    context = {
        'request': request,
    }

    context['posts'] = Post.objects.filter(forum = forum).order_by('post_date')

    return context