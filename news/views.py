from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from log.models import Log
from log.mixins import LogMixin
from django.core.urlresolvers import reverse, reverse_lazy

from .models import News
from .forms import NewsForm

class ListNewsView(LoginRequiredMixin,LogMixin,generic.ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'news/list.html'
    context_object_name = "news"
    paginate_by = 10

    def get_queryset(self):
        news = News.objects.all()
        return news

class CreateNewsView(LoginRequiredMixin,LogMixin,generic.edit.CreateView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'


    template_name = 'news/_form.html'
    form_class = NewsForm

    def form_invalid(self, form):
    	context = super(CreateNewsView, self).form_invalid(form)
    	context.status_code = 400

    	return context
