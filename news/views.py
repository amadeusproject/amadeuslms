from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from log.models import Log
from log.mixins import LogMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages

from .models import News
from .forms import NewsForm

class VisualizeNews(LoginRequiredMixin,LogMixin,generic.ListView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    template_name = 'news/view.html'
    context_object_name = "news"

    def get_context_data(self, **kwargs):
        context = super(VisualizeNews, self).get_context_data(**kwargs)
        slug = self.kwargs.get('slug', '')
        news = News.objects.get(slug=slug)
        context['news'] = news

        return context

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
    def get_success_url(self):
        messages.success(self.request, _('News successfully created!'))

        return reverse_lazy('news:view', kwargs = {'slug': self.object.slug} )

class UpdateNewsView(LoginRequiredMixin,LogMixin,generic.UpdateView):
    pass
