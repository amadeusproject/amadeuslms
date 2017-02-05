from django import template

register = template.Library()

@register.filter(name = 'action_icon')
def action_icon(action):
	if action == "comment":
		icon = "fa-commenting-o"
	elif action == "help":
		icon = "fa-comments-o"

	return icon