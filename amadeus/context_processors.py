from themes.models import Themes

def theme(request):
	context = {}

	theme = Themes.objects.get(id = 1)

	context['theme'] = theme

	return context