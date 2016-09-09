from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from core.mixins import LogMixin

from courses.models import Course


from flask import Flask
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb

app = Flask(__name__)

# Initialize Flask-Breadcrumbs
Breadcrumbs(app=app)

@app.route('/')
@register_breadcrumb(app, '.', 'Home')
def index():
    pass

if __name__ == '__main__':
    app.run(debug=True)

class AppIndex(LoginRequiredMixin, LogMixin, TemplateView):
	log_action = "Acessar"
	log_resource = "Home"
	login_url = reverse_lazy("core:home")
	redirect_field_name = 'next'
	template_name = "home_professor.html"

	def render_to_response(self, context, **response_kwargs):
		context = {}

		if self.request.user.type_profile == 2:
			template = "home_student.html"
			context['courses'] = Course.objects.filter(user = self.request.user)
		else:
			template = self.get_template_names()
			context['courses'] = Course.objects.filter(user = self.request.user)

		context['title'] = 'Amadeus'

		return self.response_class(request = self.request, template = template, context = context, using = self.template_engine, **response_kwargs)