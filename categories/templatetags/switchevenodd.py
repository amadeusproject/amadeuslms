from django import template

register = template.Library()

class switchevenodd(template.Node):
	"""docstring for switchevenodd"""
	def __init__(self, *args):
		if args:
			print(args)
		
	def render(self, context):
		
		context['switch'] = not context['switch']
		return ''

register.tag('switchevenodd', switchevenodd)