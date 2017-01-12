from django import template

from themes.models import Themes

register = template.Library()

@register.inclusion_tag('css_theme.html')
def css_theme():
	theme = Themes.objects.get(id = 1)
	
	context = {
		'theme': theme.css_style
	}

	return context