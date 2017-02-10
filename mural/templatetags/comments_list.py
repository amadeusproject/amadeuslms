from django import template

from django.core.paginator import Paginator, EmptyPage
from django.http import Http404

from mural.models import Comment

register = template.Library()

@register.inclusion_tag('mural/_list_view_comment.html')
def comments_list(request, post):
	context = {
		'request': request,
	}

	comments = Comment.objects.filter(post = post).order_by('-last_update')

	paginator = Paginator(comments, 5)

	try:
		page_number = 1
	except ValueError:
		raise Http404

	try:
		page_obj = paginator.page(page_number)
	except EmptyPage:
		raise Http404

	context['paginator'] = paginator
	context['page_obj'] = page_obj

	context['comments'] = page_obj.object_list
	context['post_id'] = post.id

	return context