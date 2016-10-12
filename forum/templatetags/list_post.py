from django import template

from django.core.paginator import Paginator, EmptyPage

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

    posts = Post.objects.filter(forum = forum).order_by('post_date')

    paginator = Paginator(posts, 1)

    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        raise Http404

    context['paginator'] = paginator
    context['page_obj'] = page_obj

    context['posts'] = page_obj.object_list
    context['forum'] = forum

    return context