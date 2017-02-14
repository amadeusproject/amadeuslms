from django import template
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from mural.models import MuralFavorites, MuralVisualizations

register = template.Library()

@register.filter(name = 'is_edited')
def is_edited(post):
	if post.edited:
		return _("(Edited)")

	return ""

@register.filter(name = 'action_icon')
def action_icon(action):
	icon = ""

	if action == "comment":
		icon = "fa-commenting-o"
	elif action == "help":
		icon = "fa-comments-o"

	return icon

@register.filter(name = 'fav_label')
def fav_label(post, user):
	if MuralFavorites.objects.filter(post = post, user = user).exists():
		return _('Unfavorite')

	return _('Favorite')

@register.filter(name = 'fav_action')
def fav_action(post, user):
	if MuralFavorites.objects.filter(post = post, user = user).exists():
		return "unfavorite"

	return "favorite"

@register.filter(name = 'fav_class')
def fav_class(post, user):
	if MuralFavorites.objects.filter(post = post, user = user).exists():
		return "btn_unfav"

	return "btn_fav"

@register.filter(name = 'unviewed')
def unviewed(category, user):
	count = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__categorypost__space = category) | Q(comment__post__categorypost__space = category))).count()

	return count